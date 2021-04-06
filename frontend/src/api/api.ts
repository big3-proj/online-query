import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';

export default function setup(): void {
  Vue.use(VueAxios, axios);
  Vue.axios.interceptors.response.use(
    (res) => {
      if (!`${res.status}`.startsWith('2')) {
        throw res;
      }
      return res.data;
    },
    (error) => { throw error; },
  );
}
