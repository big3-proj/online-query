<template>
  <div>
    <p>使用資料集為 2021/5/18~2021/05/25 約 25000 篇文章</p>
    <div class="pagination">
      <router-link :to="{ query: { page: page - 1 } }">&laquo;</router-link>
      <router-link
        v-for="pg in pagelist"
        :key="pg"
        :to="{ query: { page: pg } }"
        :class="{ active: pg === page }"
        >{{ pg }}
      </router-link>
      <router-link :to="{ query: { page: page + 1 } }">&raquo;</router-link>
    </div>
    <p v-if="isLoading">loading...</p>
    <ul v-else>
      <li v-for="post in posts" :key="post.articlePid">
        <router-link :to="`/post/${post.articlePid}`">
          {{ `${post.articleTitle}（${totalUser(post.messages)} 人參與）` }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import agent from '../api/agent';

function totalUser(messages) {
  return new Set(messages.map((msg) => msg.pushAuthorUid)).size;
}

export default {
  data() {
    return {
      posts: [],
      totalUser,
      page: 1,
      offset: 0,
      count: 15,
      isLoading: true,
    };
  },
  computed: {
    pagelist() {
      const list = [this.page - 2, this.page - 1, this.page];
      for (let i = this.page + 1; i < this.page + 5; i += 1) {
        list.push(i);
      }
      const validList = list.filter((p) => p > 0);
      return validList.slice(0, 5);
    },
  },
  watch: {
    '$route.query.page': {
      handler() {
        this.changePage();
      },
      immediate: true,
    },
  },
  methods: {
    changePage() {
      this.isLoading = true;
      this.page = Number(this.$route.query.page);
      if (this.page) {
        this.offset = 15 * this.page;
      } else {
        this.$router.replace({ query: { page: 1 } });
      }
      this.fetchData(this.page);
    },
    fetchData(page) {
      agent
        .getPosts(this.offset, this.count)
        .then((resp) => {
          if (page === this.page) {
            this.posts = resp.data;
          }
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
  },
};
</script>

<style>
.pagination {
  display: inline-block;
}

.pagination a {
  color: black;
  float: left;
  padding: 8px 16px;
  text-decoration: none;
}

.pagination a.active {
  background-color: #4caf50;
  color: white;
  border-radius: 5px;
}

.pagination a:hover:not(.active) {
  background-color: #ddd;
  border-radius: 5px;
}
</style>
