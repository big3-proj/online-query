<template>
  <div>
    <p v-if="isLoading">loading...</p>
    <div v-else>
      <h3>Post: {{ post.articlePid }}</h3>
      <router-link to="/posts">Back to posts</router-link> |
      <router-link :to="`/analyze?users=${users.join(',')}`">
        Analyze users in this post
      </router-link>
      |
      <a
        :href="`https://www.ptt.cc/bbs/Gossiping/${post.articlePid}.html`"
        target="_blank"
        rel="noreferrer noopener"
      >
        Original post
      </a>
      <h1>{{ post.articleTitle }}</h1>
      <ul>
        <li>{{ post.authorUid }}</li>
        <li>{{ post.board }}</li>
        <li>{{ post.date }}</li>
        <li>{{ post.ip }}</li>
      </ul>
      <p>{{ post.content }}</p>
      <div
        v-for="({ pushTag, pushAuthorUid, pushIpdatetime, pushContent }, index) in post.messages"
        :key="index"
        style="margin-top: 20px"
      >
        <p>
          {{ index }} 樓 {{ pushTag }} {{ pushAuthorUid }} {{ '\t' + pushContent + '\t' }}
          {{ pushIpdatetime }}
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
      .map((message) => message.pushAuthorUid)
      .concat(this.post.authorUid);
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
