import Vue from 'vue';
import VueRouter, { RouteConfig } from 'vue-router';
import Home from '../views/Home.vue';
import Posts from '../views/Posts.vue';
import Post from '../views/Post.vue';
import Analyze from '../views/Analyze.vue';
import Wordcloud from '../views/Wordcloud.vue';
import Wordclouds from '../views/Wordclouds.vue';

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/posts',
    name: 'Posts',
    component: Posts,
  },
  {
    path: '/post/:id',
    name: 'Post',
    component: Post,
  },
  {
    path: '/analyze',
    name: 'Analyze',
    component: Analyze,
  },
  {
    path: '/wordcloud',
    name: 'Wordcloud',
    component: Wordcloud,
  },
  {
    path: '/wordclouds',
    name: 'Wordclouds',
    component: Wordclouds,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
