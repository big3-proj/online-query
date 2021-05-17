<template>
  <div>
    <div class="flex justify-center">
      <p v-if="isLoading">loading...</p>
    </div>
    <div class="flex flex-row flex-nowrap justify-center" style="height: 500px">
      <div id="tsne-plot" :style="{ width: tsneWidth + 40, height: tsneHeight + 40 }">
        <svg :width="tsneWidth" :height="tsneHeight" :style="{ border: '1px solid #000' }" />
      </div>
      <div class="w-full h-full overflow-hidden px-1 ml-2 border">
        <div>selected users: {{ selectedUsers.length }}</div>
        <div class="overflow-auto h-full">
          <ul>
            <li v-for="{ id } in sortedSelectedUsers" :key="id">{{ id }}</li>
          </ul>
        </div>
      </div>
      <div class="w-full h-full overflow-hidden px-1 ml-2 border">
        <div class="flex flex-row justify-center">
          <button @click="tab = 1" class="btn">Wordcloud</button>
          <button @click="tab = 0" class="btn" style="margin-left: 20px">Heat map</button>
        </div>
        <div class="search" v-if="tab === 1">
          <label for="query" style="margin-right: 10px">Filter</label>
          <input
            id="query"
            v-model="searchText"
            type="text"
            style="height: 24px; font-size: 20px"
          />
        </div>
      </div>
    </div>
    <div class="flex justify-center">
      <p>{{ ['Heat map', 'Wordcloud'][tab] }}</p>
    </div>
    <Heatmap v-if="tab === 0" :users="sortedSelectedUsers" />
    <div v-if="tab === 1" class="container">
      <Wordcloud
        v-for="userId in sortedSelectedUsers.map((u) => u.id)"
        :key="userId"
        :userId="userId"
        :focusedContent="searchText"
        :width="450"
        :height="450"
      />
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import Wordcloud from '../components/Wordcloud.vue';
import Heatmap from '../components/Heatmap.vue';
import agent from '../api/agent';

export default {
  components: { Wordcloud, Heatmap },
  data: () => ({
    tab: 1,
    plot: null,
    searchText: '',
    isLoading: true,
    selectedUsers: [],
    tsneWidth: 700,
    tsneHeight: 500,
  }),
  computed: {
    sortedSelectedUsers() {
      return this.selectedUsers
        .slice()
        .sort((a, b) => (a.id.toUpperCase() <= b.id.toUpperCase() ? -1 : 1));
    },
    analyzeUsers() {
      return this.$route.query.users && this.$route.query.users.split(',');
    },
  },
  mounted() {
    agent
      .getAnalyze(this.analyzeUsers)
      .then((resp) => {
        this.plot = resp.data;
        this.drawTSNE();
      })
      .finally(() => {
        this.isLoading = false;
      });
  },
  methods: {
    drawTSNE() {
      const vue = this;
      const data = this.plot;
      const coordX = data.map((d) => d.coord[0]);
      const coordY = data.map((d) => d.coord[1]);
      const [minX, maxX] = [Math.min(...coordX), Math.max(...coordX)];
      const [minY, maxY] = [Math.min(...coordY), Math.max(...coordY)];
      const margin = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20,
      };
      const fullWidth = this.tsneWidth;
      const width = fullWidth - margin.left - margin.right;
      const fullHeight = this.tsneHeight;
      const height = fullHeight - margin.top - margin.bottom;
      const dotRadius = 7;

      const x = d3
        .scaleLinear()
        .domain([minX, maxX])
        .range([0 + dotRadius, width - dotRadius]);
      const y = d3
        .scaleLinear()
        .domain([minY, maxY])
        .range([height - dotRadius, 0 + dotRadius]);
      const color = d3
        .scaleOrdinal()
        .domain(['midnight', 'morning', 'afternoon', 'evening'])
        .range(['#003f5c', '#7a5195', '#ef5675', '#ffa600']);

      const svg = d3.select('#tsne-plot > svg');

      const main = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

      // Add dots
      const dotsGroup = main.append('g');
      const dots = dotsGroup
        .selectAll('dot')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx', (d) => x(d.coord[0]))
        .attr('cy', (d) => y(d.coord[1]))
        .attr('r', 7)
        .style('fill', (d) => color(d.label))
        .style('opacity', 0.5);

      // A function that return TRUE or FALSE according if a dot is in the selection or not
      function isBrushed(brushCoords, cx, cy) {
        const x0 = brushCoords[0][0];
        const x1 = brushCoords[1][0];
        const y0 = brushCoords[0][1];
        const y1 = brushCoords[1][1];
        return x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;
      }

      // Function that is triggered when brushing is performed
      function updateChart() {
        const extent = d3.event.selection;
        const selected = dots.filter((d) => isBrushed(extent, x(d.coord[0]), y(d.coord[1])));
        dots.classed('selected', false);
        selected.classed('selected', true);
        // eslint-disable-next-line no-underscore-dangle
        vue.selectedUsers = selected.nodes().map((node) => node.__data__);
      }

      /**
       * call brushing and zooming on same element will make brush disabled
       * more precisely, read this https://stackoverflow.com/questions/59753784/d3-js-allow-brushing-and-zooming-on-same-chart
       */
      // Add brushing
      dotsGroup.call(
        d3
          .brush()
          .extent([
            [0, 0],
            [width, height],
          ])
          .on('brush', updateChart),
      );
      // Add Zooming
      svg.call(
        d3.zoom().on('zoom', () => {
          main.attr('transform', d3.event.transform);
        }),
      );

      // Add legend
      const legendX = fullWidth - 120;
      const legendY = 30;
      const labels = ['midnight', 'morning', 'afternoon', 'evening'];
      labels.forEach((l, idx) => {
        svg
          .append('circle')
          .attr('cx', legendX)
          .attr('cy', 10 + legendY * idx)
          .attr('r', dotRadius)
          .style('fill', color(l));
        svg
          .append('text')
          .attr('x', legendX + 20)
          .attr('y', 10 + legendY * idx)
          .text(l)
          .style('fill', 'black')
          .style('font-size', '15px')
          .attr('alignment-baseline', 'middle');
      });
    },
  },
};
</script>

<style>
.selected {
  opacity: 1 !important;
  stroke: black;
  stroke-width: 1px;
}
.flex {
  display: flex;
}
.flex-row {
  flex-direction: row;
}
.justify-center {
  justify-content: center;
}
.flex-nowrap {
  flex-wrap: nowrap;
}
.w-full {
  width: 100%;
}
.h-full {
  height: 100%;
}
.overflow-hidden {
  overflow: hidden;
}
.overflow-auto {
  overflow: auto;
}
.px-1 {
  padding: 0 4px;
}
.ml-2 {
  margin-left: 8px;
}
.border {
  border: 1px solid #c3c3c3;
}
.btn {
  width: 100%;
  margin-top: 5px;
  background-color: #ddd;
  border: none;
  color: black;
  padding: 15px 32px;
  text-align: center;
  font-size: 16px;
}
.search {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}
</style>
