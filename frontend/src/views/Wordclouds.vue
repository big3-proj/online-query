<template>
  <div>
    <input v-model="searchText" type="text" style="height: 24px; font-size: 20px;">
    <div class="container">
      <Wordcloud
        v-for="userId in ['ispy03532003', 'go190214', 'AdagakiAki', 'g10', 'exceedMyself']"
        :key="userId"
        :userId="userId"
        :focusedContent="searchText"
        :width="400"
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
});
</script>

<style lang="css" scoped>
.container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}
</style>
