<template>
  <div>
    <input v-model="searchText" type="text" style="height: 24px; font-size: 20px;">
    <Wordcloud
      v-for="userId in ['go190214', 'ispy03532003', 'AdagakiAki', 'g10', 'exceedMyself']"
      :key="userId"
      :userId="userId"
      :focus="searchText"
    />
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Wordcloud from './Wordcloud.vue';

export default Vue.extend({
  components: { Wordcloud },
  data() {
    return {
      searchText: '',
    };
  },
});
</script>
