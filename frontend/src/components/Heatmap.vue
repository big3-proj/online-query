<template>
  <div id="heatmap" />
</template>

<script>
import * as d3 from 'd3';
import { interpolatePurples } from 'd3-scale-chromatic';

export default {
  props: {
    users: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    heatmapSortedUsers: [],
    heatmapUnitHeight: 50,
    heatmapSortCounter: new Array(24).fill(0),
  }),
  mounted() {
    this.drawHeatmap();
  },
  watch: {
    users: {
      handler() {
        this.heatmapSortedUsers = this.users;
        this.drawHeatmap();
      },
      immediate: true,
    },
  },
  computed: {
    heatmapWidth() {
      return this.heatmapUnitHeight * 24;
    },
  },
  methods: {
    sortHeatmap(d) {
      this.heatmapSortCounter[d] += 1;
      switch (this.heatmapSortCounter[d] % 3) {
        case 0:
          // Lexicographic order
          this.heatmapSortedUsers = this.users.slice();
          break;
        case 1:
          // Asscending order
          this.heatmapSortedUsers = this.users
            .slice()
            .sort((a, b) => b.activities[d] - a.activities[d]);
          break;
        case 2:
          // Descending order
          this.heatmapSortedUsers = this.users
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
            value: a * 5 + Math.random() * 2,
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
      const height = this.heatmapUnitHeight * this.users.length;
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
        .domain(d3.extent(values));

      console.log(values);

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
</script>
