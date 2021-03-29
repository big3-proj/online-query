import Vue from 'vue';
import { AxiosResponse } from 'axios';
import {
  IPosts, IPost, ITsnePlot, IWordcloud,
} from '../types';

export default {
  getAnalyze: (): Promise<AxiosResponse<ITsnePlot[]>> => Vue.axios.get<ITsnePlot[]>('/analyze'),
  getPosts: (): Promise<AxiosResponse<IPosts[]>> => Vue.axios.get<IPosts[]>('/posts'),
  getPost: (id: string): Promise<AxiosResponse<IPost>> => Vue.axios.get<IPost>(`/post/${id}`),
  getWordcloud: (): Promise<AxiosResponse<IWordcloud[]>> => Vue.axios.get<IWordcloud[]>('/wordcloud'),
};
