<template>
  <div>
    <Wordcloud
      v-for="userId in ['go190214', 'ispy03532003', 'AdagakiAki', 'g10', 'exceedMyself']"
      :key="userId"
      :userId="userId"
    />
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Wordcloud from './Wordcloud.vue';

export default Vue.extend({
  components: { Wordcloud },
})
</script>