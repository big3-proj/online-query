<template>
  <div>
    <p v-if="isLoading">loading...</p>
    <div :id="`wordcloud-${userId}`" :style="{ width: width, height: height }">
      <h5>{{ userId }}</h5>
      <svg class="wordcloud" />
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import agent from '../api/agent';

export default {
  props: {
    userId: {
      type: String,
      default: 'g10',
    },
  },

  data() {
    return {
      plot: null,
      isLoading: true,
      width: 800,
      height: 400,
    };
  },

  mounted() {
    agent
      .getWordcloud(this.userId)
      .then((resp) => {
        this.plot = resp.data;
        this.draw();
      })
      .finally(() => {
        this.isLoading = false;
      });
  },

  methods: {
    draw() {
      const data = this.plot.sort((a, b) => (a.freq > b.freq ? -1 : 1));
      const [minFreq, maxFreq] = [data[data.length - 1].freq, data[0].freq];
      // set the dimensions and margins of the graph
      const margin = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20,
      };
      const width = this.width - margin.left - margin.right;
      const size = d3.scaleLinear().domain([minFreq, maxFreq]).range([15, 80]);

      // append the svg object to the body of the page
      const svg = d3
        .select(`#wordcloud-${this.userId} > svg`)
        .attr('style', 'outline: thin solid black;')
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      svg
        .selectAll('text')
        .data(data)
        .enter()
        .append('text')
        .attr('text-anchor', 'start')
        .style('font-size', (d) => size(d.freq))
        .style('fill', '#003f5c')
        .text((d) => d.word)
        .append('tspan')
        .style('font-size', (d) => (size(d.freq) / 3) * 2)
        .style('fill', '#bc5090')
        .text((d) => d.freq)
        .attr('dy', '-0.6em');

      let x = 0;
      let y = 0;
      svg.selectAll('text').attr('transform', function (d, i) {
        if (i > 0) {
          x = this.previousElementSibling.getBoundingClientRect().right - margin.left;
        } else {
          y += parseInt(this.style.fontSize, 10) - 15;
        }
        if (x + this.getComputedTextLength() > width) {
          x = 0;
          y += this.getBoundingClientRect().height;
        }
        return `translate(${x}, ${y})`;
      });
    },
  },
};
</script>

<style scoped>
.wordcloud {
  width: 800px;
  height: 400px;
}
</style>
