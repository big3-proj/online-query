import Vue from 'vue';
import App from './App.vue';
import router from './router';
import setupAxios from './api/api';

Vue.config.productionTip = false;

setupAxios();

new Vue({
  router,
  render: (h) => h(App),
}).$mount('#app');
