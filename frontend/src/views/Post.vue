<template>
  <div>
    <h3>Post: {{ $route.params.id }}</h3>
    <router-link to="/posts">Back to posts</router-link> |
    <router-link :to="`/analyze?users=${users.join(',')}`">Analyze users in this post</router-link>
    <p v-if="isLoading">loading...</p>
    <div v-else>
      <h1>{{ post.article_title }}</h1>
      <ul>
        <li>{{ post.author_id }}</li>
        <li>{{ post.board }}</li>
        <li>{{ post.date }}</li>
        <li>{{ post.ip }}</li>
      </ul>
      <p>{{ post.content }}</p>
      <div
        v-for="({ push_tag, push_userid, push_ipdatetime, push_content }, index) in post.messages"
        :key="index"
        style="margin-top: 20px"
      >
        <p>
          {{ index }} 樓 {{ push_tag }} {{ push_userid }} {{ '\t' + push_content + '\t' }}
          {{ push_ipdatetime }}
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import agent from '../api/agent';
import { IPost } from '../types';

@Component
export default class Post extends Vue {
  post: IPost | null = null;

  isLoading = true;

  get users(): string[] {
    if (!this.post) return [];
    const participants = this.post.messages
      .map((message) => message.push_userid)
      .concat(this.post.author_id);
    const distinctParticipants = [...new Set(participants)];
    return distinctParticipants;
  }

  mounted(): void {
    agent
      .getPost(this.$route.params.id)
      .then((resp): void => {
        this.post = resp.data;
      })
      .finally((): void => {
        this.isLoading = false;
      });
  }
}
</script>
