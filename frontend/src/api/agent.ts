import Vue from 'vue';
import { AxiosResponse } from 'axios';
import {
  IPost, ITsnePlot, IWordcloud, IRidgelineData,
} from '../types';

export default {
  getAnalyze: (users: string[]): Promise<AxiosResponse<ITsnePlot[]>> => Vue.axios.post<ITsnePlot[]>('/analyze', { users }),
  getPosts: (offset: number, count: number): Promise<AxiosResponse<IPost[]>> => Vue.axios.get<IPost[]>('/posts', { params: { offset, count } }),
  getPost: (id: string): Promise<AxiosResponse<IPost>> => Vue.axios.get<IPost>(`/post/${id}`),
  getWordcloud: (userId: string): Promise<AxiosResponse<IWordcloud[]>> => Vue.axios.get<IWordcloud[]>(`/wordcloud/${userId}`),
  getRidgeline: (users: string[], word: string): Promise<AxiosResponse<IRidgelineData>> => Vue.axios.post<IRidgelineData>('/ridgeline', { users, word }),
};
