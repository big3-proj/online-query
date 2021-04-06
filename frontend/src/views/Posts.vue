<template>
  <div>
    <p v-if="isLoading">loading...</p>
    <ul v-else>
      <li v-for="[id, post] in posts" :key="id">
        <router-link :to="`/post/${id}`">
          {{ `${post.article_title}（${count(post.messages)} 人參與）` }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import agent from '../api/agent';
import { IPosts, IPush } from '../types';

function count(messages: IPush[]): number {
  return new Set(messages.map((msg) => msg.push_userid)).size;
}

@Component
export default class Posts extends Vue {
  posts: [string, IPosts][] = [];

  count = count;

  isLoading = true;

  mounted(): void {
    agent
      .getPosts()
      .then((resp): void => {
        this.posts = Object.entries(resp.data);
      })
      .finally(() => {
        this.isLoading = false;
      });
  }
}
</script>
