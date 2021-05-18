<template>
  <div>
    <p v-if="isLoading">loading...</p>
    <ul v-else>
      <li v-for="post in posts" :key="post.articleId">
        <router-link :to="`/post/${post.articleId}`">
          {{ `${post.articleTitle}（${count(post.messages)} 人參與）` }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import agent from '../api/agent';
import { IPost, IPush } from '../types';

function count(messages: IPush[]): number {
  return new Set(messages.map((msg) => msg.pushAuthorUid)).size;
}

@Component
export default class Posts extends Vue {
  posts: IPost[] = [];

  count = count;

  isLoading = true;

  mounted(): void {
    agent
      .getPosts()
      .then((resp): void => {
        this.posts = resp.data;
      })
      .finally(() => {
        this.isLoading = false;
      });
  }
}
</script>
