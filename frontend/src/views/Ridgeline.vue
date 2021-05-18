<template>
  <div>
    <div class="flex justify-center">
      <p v-if="isLoading">loading...</p>
    </div>
    逗號分隔
    <textarea v-model="usersInput" rows="5" style="width: 50%" />
    <input v-model="word" placeholder="文字" @keydown.enter="submit" />
    <button @click="submit">submit</button>
    <svg width="1200" height="6000" />
  </div>
</template>

<script>
import * as d3 from 'd3';
import agent from '../api/agent';

export default {
  data: () => ({
    usersInput:
      'ae8656tw,asidy,coolman9972,doubleaisno1,iori2968,joker7788996,kodo5566,Ladyink,lhtltyh,maximu',
    word: '達叔',
    isLoading: true,
    data: null,
  }),
  computed: {
    users() {
      return this.usersInput.split(',');
    },
  },
  mounted() {
    if (this.$route.query.usersInput) this.usersInput = this.$route.query.usersInput;
    if (this.$route.query.word) this.word = this.$route.query.word;
    this.submit();
  },
  methods: {
    submit() {
      this.isLoading = true;
      agent
        .getRidgeline(this.users, this.word)
        .then((resp) => {
          this.data = resp.data;
          this.drawRidgeline();
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    drawRidgeline() {
      d3.selectAll('svg > *').remove();
      const data = Object.entries(this.data);
      const svg = d3.select('svg');
      const width = 500;
      const height = 50;
      const margin = {
        left: 200,
      };

      const distr = svg.append('g').attr('transform', `translate(${margin.left}, 0)`);

      const x = d3.scaleLinear().domain([0, 364]).range([0, width]);
      const y = d3
        .scaleLinear()
        .domain([0, d3.max(data.map((d) => d3.max(d[1])))])
        .range([height, 0]);

      const area = d3
        .area()
        .x((d, i) => x(i))
        .y0(y(0))
        .y1((d) => y(d))
        .curve(d3.curveMonotoneX);

      data.forEach(([user, d], index) => {
        const h = height * (index + 1);
        distr
          .append('text')
          .attr('transform', `translate(-50, ${h + height / 2})`)
          .attr('font-size', '15px')
          .attr('text-anchor', 'middle')
          .text(user);
        distr
          .append('path')
          .attr('transform', `translate(0, ${h})`)
          .attr('fill', 'steelblue')
          .attr('stroke', 'black')
          .attr('stroke-width', 0.7)
          .attr('d', area(d));
      });
    },
  },
};
</script>

<style></style>
