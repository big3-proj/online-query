import Vue from 'vue';
import { AxiosResponse } from 'axios';
import {
  IPost, ITsnePlot, IWordcloud,
} from '../types';

export default {
  getAnalyze: (users: string[]): Promise<AxiosResponse<ITsnePlot[]>> => Vue.axios.post<ITsnePlot[]>('/analyze', { users }),
  getPosts: (): Promise<AxiosResponse<IPost[]>> => Vue.axios.get<IPost[]>('/posts'),
  getPost: (id: string): Promise<AxiosResponse<IPost>> => Vue.axios.get<IPost>(`/post/${id}`),
  getWordcloud: (userId: string): Promise<AxiosResponse<IWordcloud[]>> => Vue.axios.get<IWordcloud[]>(`/wordcloud/${userId}`),
};
