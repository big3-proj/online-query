<template>
  <div>
    <p v-if="isLoading">loading...</p>
    <div class="flex flex-row flex-nowrap h-700">
      <div id="tsne-plot" :style="{ width: '1140px', height: '740px' }">
        <svg :style="{ width: tsneWidth, height: tsneHeight, border: '1px solid #000' }" />
      </div>
      <div class="w-full h-full overflow-hidden px-1 ml-2 border">
        <div>selected users: {{ selectedUsers.length }}</div>
        <div class="overflow-auto h-full">
          <ul>
            <li v-for="{ id } in sortedSelectedUsers" :key="id">{{ id }}</li>
          </ul>
        </div>
      </div>
    </div>
    <button @click="tab = 0">heatmap</button>
    <button @click="tab = 1">wordcloud</button>
    <div v-if="tab === 0" id="heatmap" />
    <div v-if="tab === 1">
      <Wordcloud
        v-for="userId in ['go190214', 'ispy03532003', 'AdagakiAki', 'g10', 'exceedMyself']"
        :key="userId"
        :userId="userId"
      />
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import { interpolatePurples } from 'd3-scale-chromatic';
import Wordcloud from '../components/Wordcloud.vue';
import agent from '../api/agent';

export default {
  components: { Wordcloud },
  data: () => ({
    tab: 1,
    plot: null,
    isLoading: true,
    selectedUsers: [],
    heatmapSortedUsers: [],
    tsneWidth: 1100,
    tsneHeight: 700,
    heatmapUnitHeight: 50,
    heatmapSortCounter: new Array(24).fill(0),
  }),
  watch: {
    selectedUsers() {
      this.heatmapSortedUsers = this.sortedSelectedUsers;
      this.drawHeatmap();
    },
  },
  computed: {
    sortedSelectedUsers() {
      return this.selectedUsers
        .slice()
        .sort((a, b) => (a.id.toUpperCase() <= b.id.toUpperCase() ? -1 : 1));
    },
    heatmapWidth() {
      return this.heatmapUnitHeight * 24;
    },
  },
  mounted() {
    agent
      .getAnalyze()
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

      const x = d3.scaleLinear().domain([minX, maxX]).range([0, width]);
      const y = d3.scaleLinear().domain([minY, maxY]).range([height, 0]);
      const color = d3
        .scaleOrdinal()
        .domain(['midnight', 'morning', 'afternoon', 'evening'])
        .range(['#003f5c', '#7a5195', '#ef5675', '#ffa600']);

      const svg = d3
        .select('#tsne-plot > svg')
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      // Add dots
      const dots = svg
        .append('g')
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
        const x0 = brushCoords[0][0] - margin.left;
        const x1 = brushCoords[1][0] - margin.left;
        const y0 = brushCoords[0][1] - margin.top;
        const y1 = brushCoords[1][1] - margin.top;
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

      // Add brushing
      d3.select('#tsne-plot > svg').call(
        d3
          .brush()
          .extent([
            [0, 0],
            [fullWidth, fullHeight],
          ])
          .on('brush', updateChart),
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
          .attr('r', 7)
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
    sortHeatmap(d) {
      this.heatmapSortCounter[d] += 1;
      switch (this.heatmapSortCounter[d] % 3) {
        case 0:
          // Lexicographic order
          this.heatmapSortedUsers = this.sortedSelectedUsers.slice();
          break;
        case 1:
          // Asscending order
          this.heatmapSortedUsers = this.sortedSelectedUsers
            .slice()
            .sort((a, b) => b.activities[d] - a.activities[d]);
          break;
        case 2:
          // Descending order
          this.heatmapSortedUsers = this.sortedSelectedUsers
            .slice()
            .sort((a, b) => a.activities[d] - b.activities[d]);
          break;
        default:
          break;
      }
      this.drawHeatmap();
    },
    drawHeatmap() {
      d3.selectAll('#heatmap > *').remove();

      const vue = this;
      const data = this.heatmapSortedUsers
        .map((u) =>
          u.activities.map((a, i) => ({
            row: u.id,
            col: i,
            value: a,
          })),
        )
        .reduce((a, b) => [...a, ...b], []);
      const values = data.map((d) => d.value);
      const margin = {
        top: 50,
        right: 20,
        bottom: 20,
        left: 120,
      };
      const width = this.heatmapWidth;
      const fullWidth = width + margin.left + margin.right;
      const height = this.heatmapUnitHeight * this.selectedUsers.length;
      const fullHeight = height + margin.top + margin.bottom;

      const svg = d3
        .select('#heatmap')
        .append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const x = d3
        .scaleBand()
        .range([0, width])
        .domain(data.map((d) => d.col))
        .padding(0.05);
      svg
        .append('g')
        .style('font-size', 15)
        .attr('id', 'axis-x')
        .call(d3.axisTop(x).tickSize(0))
        .select('.domain')
        .remove();
      d3.selectAll('#axis-x > g').on('click', (d) => vue.sortHeatmap(d));

      const y = d3
        .scaleBand()
        .range([0, height])
        .domain(data.map((d) => d.row))
        .padding(0);
      svg
        .append('g')
        .style('font-size', 15)
        .call(d3.axisLeft(y).tickSize(0))
        .select('.domain')
        .remove();

      const color = d3
        .scaleSequential(interpolatePurples)
        .domain([Math.min(...values), Math.max(...values)]);

      svg
        .selectAll()
        .data(data, (d) => `${d.row},${d.col}`)
        .enter()
        .append('rect')
        .attr('x', (d) => x(d.col))
        .attr('y', (d) => y(d.row))
        .attr('rx', 4)
        .attr('ry', 4)
        .attr('width', x.bandwidth())
        .attr('height', x.bandwidth())
        .style('fill', (d) => color(d.value))
        .style('stroke-width', 4)
        .style('stroke', 'none')
        .style('opacity', 0.8);
    },
  },
};
// import { Component, Watch, Vue } from 'vue-property-decorator';
// import * as d3 from 'd3';
// // import * as d3Color from 'd3-color';
// // import from 'd3-interpolate';
// import { interpolatePurples } from 'd3-scale-chromatic';
// import agent from '../api/agent';
// import { ITsnePlot, IHeatmapPlot } from '../types';

// @Component
// export default class Posts extends Vue {
//   plot: ITsnePlot[] = [];

//   selectedUsers: ITsnePlot[] = [];

//   heatmapSortedUsers: ITsnePlot[] = [];

//   tsneWidth = 1100;

//   tsneHeight = 700;

//   heatmapUnitHeight = 50;

//   heatmapSortCounter: number[] = new Array(24).fill(0);

//   isLoading = true;

//   mounted(): void {
//     agent
//       .getAnalyze()
//       .then((resp): void => {
//         this.plot = resp.data;
//         this.drawTSNE();
//       })
//       .finally(() => {
//         this.isLoading = false;
//       });
//   }

//   @Watch('selectedUsers')
//   nameChanged(): void {
//     this.heatmapSortedUsers = this.sortedSelectedUsers;
//     this.drawHeatmap();
//   }

//   get sortedSelectedUsers(): ITsnePlot[] {
//     return this.selectedUsers
//       .slice()
//       .sort((a, b) => (a.id.toUpperCase() <= b.id.toUpperCase() ? -1 : 1));
//   }

//   get heatmapWidth(): number {
//     return this.heatmapUnitHeight * 24;
//   }

//   drawTSNE(): void {
//     const vue = this;
//     const data = this.plot;
//     const coordX = data.map((d) => d.coord[0]);
//     const coordY = data.map((d) => d.coord[1]);
//     const [minX, maxX] = [Math.min(...coordX), Math.max(...coordX)];
//     const [minY, maxY] = [Math.min(...coordY), Math.max(...coordY)];
//     const margin = {
//       top: 20,
//       right: 20,
//       bottom: 20,
//       left: 20,
//     };
//     const fullWidth = this.tsneWidth;
//     const width = fullWidth - margin.left - margin.right;
//     const fullHeight = this.tsneHeight;
//     const height = fullHeight - margin.top - margin.bottom;

//     const x = d3.scaleLinear().domain([minX, maxX]).range([0, width]);
//     const y = d3.scaleLinear().domain([minY, maxY]).range([height, 0]);
//     const color = d3
//       .scaleOrdinal()
//       .domain(['midnight', 'morning', 'afternoon', 'evening'])
//       .range(['#003f5c', '#7a5195', '#ef5675', '#ffa600']);

//     const svg = d3
//       .select('#tsne-plot')
//       .append('svg')
//       .attr('width', fullWidth)
//       .attr('height', fullHeight)
//       .style('border', '1px solid #000')
//       .append('g')
//       .attr('transform', `translate(${margin.left},${margin.top})`);

//     // Add dots
//     const dots = svg
//       .append('g')
//       .selectAll('dot')
//       .data<ITsnePlot>(data)
//       .enter()
//       .append('circle')
//       .attr('cx', (d: ITsnePlot) => x(d.coord[0]))
//       .attr('cy', (d: ITsnePlot) => y(d.coord[1]))
//       .attr('r', 7)
//       .style('fill', (d: ITsnePlot): string => String(color(d.label)))
//       .style('opacity', 0.5);

//     // A function that return TRUE or FALSE according if a dot is in the selection or not
//     function isBrushed(brushCoords: number[][], cx: number, cy: number): boolean {
//       const x0 = brushCoords[0][0] - margin.left;
//       const x1 = brushCoords[1][0] - margin.left;
//       const y0 = brushCoords[0][1] - margin.top;
//       const y1 = brushCoords[1][1] - margin.top;
//       return x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;
//     }

//     // Function that is triggered when brushing is performed
//     function updateChart(): void {
//       const extent: number[][] = d3.event.selection;
//       console.log('extent:', extent);
//       const selected = dots.filter((d: ITsnePlot) =>
//         isBrushed(extent, x(d.coord[0]), y(d.coord[1])),
//       );
//       dots.classed('selected', false);
//       selected.classed('selected', true);
//       // eslint-disable-next-line no-underscore-dangle
//       vue.selectedUsers = selected.nodes().map((node: any) => node.__data__);
//     }

//     // Add brushing
//     d3.select('#tsne-plot > svg').call(
//       d3
//         .brush()
//         .extent([
//           [0, 0],
//           [fullWidth, fullHeight],
//         ])
//         .on('brush', updateChart),
//     );

//     // Add legend
//     const legendX = fullWidth - 120;
//     const legendY = 30;
//     const labels = ['midnight', 'morning', 'afternoon', 'evening'];
//     labels.forEach((l, idx) => {
//       svg
//         .append('circle')
//         .attr('cx', legendX)
//         .attr('cy', 10 + legendY * idx)
//         .attr('r', 7)
//         .style('fill', String(color(l)));
//       svg
//         .append('text')
//         .attr('x', legendX + 20)
//         .attr('y', 10 + legendY * idx)
//         .text(l)
//         .style('fill', 'black')
//         .style('font-size', '15px')
//         .attr('alignment-baseline', 'middle');
//     });
//   }

//   sortHeatmap(d: number): void {
//     this.heatmapSortCounter[d] += 1;
//     switch (this.heatmapSortCounter[d] % 3) {
//       case 0:
//         // Lexicographic order
//         this.heatmapSortedUsers = this.sortedSelectedUsers.slice();
//         break;
//       case 1:
//         // Asscending order
//         this.heatmapSortedUsers = this.sortedSelectedUsers
//           .slice()
//           .sort((a, b) => b.activities[d] - a.activities[d]);
//         break;
//       case 2:
//         // Descending order
//         this.heatmapSortedUsers = this.sortedSelectedUsers
//           .slice()
//           .sort((a, b) => a.activities[d] - b.activities[d]);
//         break;
//       default:
//         break;
//     }
//     this.drawHeatmap();
//   }

//   drawHeatmap(): void {
//     d3.selectAll('#heatmap > *').remove();

//     const vue = this;
//     const data = this.heatmapSortedUsers
//       .map((u) =>
//         u.activities.map(
//           (activity: number, index: number): IHeatmapPlot => ({
//             row: u.id,
//             col: index,
//             value: activity,
//           }),
//         ),
//       )
//       .reduce((a, b) => [...a, ...b], []);
//     const values = data.map((d: IHeatmapPlot) => d.value);
//     const margin = {
//       top: 50,
//       right: 20,
//       bottom: 20,
//       left: 120,
//     };
//     const width = this.heatmapWidth;
//     const fullWidth = width + margin.left + margin.right;
//     const height = this.heatmapUnitHeight * this.selectedUsers.length;
//     const fullHeight = height + margin.top + margin.bottom;

//     const svg = d3
//       .select('#heatmap')
//       .append('svg')
//       .attr('width', fullWidth)
//       .attr('height', fullHeight)
//       .append('g')
//       .attr('transform', `translate(${margin.left},${margin.top})`);

//     const x = d3
//       .scaleBand()
//       .range([0, width])
//       .domain(data.map((d: IHeatmapPlot): string => String(d.col)))
//       .padding(0.05);
//     svg
//       .append('g')
//       .style('font-size', 15)
//       .attr('id', 'axis-x')
//       .call(d3.axisTop(x).tickSize(0))
//       .select('.domain')
//       .remove();
//     d3.selectAll('#axis-x > g').on('click', (d: unknown): void => vue.sortHeatmap(Number(d)));

//     const y = d3
//       .scaleBand()
//       .range([0, height])
//       .domain(data.map((d: IHeatmapPlot): string => d.row))
//       .padding(0);
//     svg
//       .append('g')
//       .style('font-size', 15)
//       .call(d3.axisLeft(y).tickSize(0))
//       .select('.domain')
//       .remove();

//     const color = d3
//       .scaleSequential(interpolatePurples)
//       .domain([Math.min(...values), Math.max(...values)]);

//     svg
//       .selectAll()
//       .data<IHeatmapPlot>(
//         data,
//         (d: IHeatmapPlot | undefined): string => `${d && d.row},${d && d.col}`,
//       )
//       .enter()
//       .append('rect')
//       .attr('x', (d: IHeatmapPlot): number => Number(x(String(d.col))))
//       .attr('y', (d: IHeatmapPlot): number => Number(y(d.row)))
//       .attr('rx', 4)
//       .attr('ry', 4)
//       .attr('width', x.bandwidth())
//       .attr('height', x.bandwidth())
//       .style('fill', (d: IHeatmapPlot): string => color(d.value))
//       .style('stroke-width', 4)
//       .style('stroke', 'none')
//       .style('opacity', 0.8);
//   }
// }
//
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
.flex-nowrap {
  flex-wrap: nowrap;
}
.w-full {
  width: 100%;
}
.h-full {
  height: 100%;
}
.h-700 {
  height: 700px;
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
</style>
