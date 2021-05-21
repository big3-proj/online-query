<template>
  <div>
    <div class="search">
      <label for="query" style="margin-right: 10px;">Filter</label>
      <input id="query" v-model="searchText" type="text" style="height: 24px; font-size: 20px;">
    </div>
    <div class="container">
      <Wordcloud
        v-for="userId in ['ispy03532003', 'go190214', 'AdagakiAki', 'g10', 'exceedMyself']"
        :key="userId"
        :userId="userId"
        :focusedContent="searchText"
        :width="450"
        :height="450"
        @update-focusedContent="updateSearchText"
      />
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Wordcloud from '../components/Wordcloud.vue';

export default Vue.extend({
  components: { Wordcloud },
  data() {
    return {
      searchText: '',
    };
  },
  methods: {
    updateSearchText(searchText) { this.searchText = searchText; },
  },
});
</script>

<style lang="css" scoped>
.search {
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
