<template>
  <div>
    <h3>Post: {{ $route.params.id }}</h3>
    <router-link to="/posts">Back to posts</router-link>
    <p v-if="isLoading">loading...</p>
    <div v-else>
      <h1>{{ post.article_title }}</h1>
      <ul>
        <li>{{ post.author }}</li>
        <li>{{ post.board }}</li>
        <li>{{ post.date }}</li>
        <li>{{ post.ip }}</li>
        <li>
          推/噓/回：{{ post.message_count.push }}/{{ post.message_count.boo }}/{{
            post.message_count.neutral
          }}
        </li>
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

  mounted(): void {
    agent
      .getPost(this.$route.params.id)
      .then((resp): void => {
        this.post = resp.data;
      })
      .finally(() => {
        this.isLoading = false;
      });
  }
}
</script>
