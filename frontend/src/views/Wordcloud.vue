<template>
  <div>
    <h1>This is wordcloud page</h1>
    <p v-if="isLoading">loading...</p>
    <div id="plot" />
  </div>
</template>

<script>
import * as d3 from 'd3';
import agent from '../api/agent';

export default {
  data() {
    return {
      plot: null,
      isLoading: true,
    };
  },

  mounted() {
    agent
      .getWordcloud()
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
      const width = 800 - margin.left - margin.right;
      const height = 800 - margin.top - margin.bottom;
      let x = 0;
      let y = 60;
      const size = d3.scaleLinear().domain([minFreq, maxFreq]).range([15, 80]);

      // append the svg object to the body of the page
      const svg = d3
        .select('#plot')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      svg
        .append('g')
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

      svg.selectAll('text').attr('transform', function (d, i) {
        if (i) x = this.previousElementSibling.getBoundingClientRect().right - margin.left;
        if (x + this.getComputedTextLength() > width) {
          x = 0;
          y += this.getBoundingClientRect().height * 1.2;
          // y = this.previousElementSibling.getBoundingClientRect().bottom;
          // y += this.getBoundingClientRect().height * 0.5;
        }
        return `translate(${x}, ${y})`;
      });
    },
  },
};
</script>
