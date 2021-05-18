export interface IPush {
  pushContent: string,
  pushIpdatetime: string,
  pushTag: string,
  pushAuthorId: number,
  pushAuthorUid: string,
}

export interface IPost {
  articleId: number,
  articlePid: string,
  articleUitle: string,
  authorId: number,
  authorUid: string,
  board: string,
  content: string,
  date: Date,
  ip: string,
  messages: IPush[],
}

export interface IPosts {
  [key: string]: IPost,
}

export interface ITsnePlot {
  activities: number[],
  coord: number[],
  id: string,
  label: 'morning' | 'afternoon' | 'evening' | 'midnight'
}

export interface IHeatmapPlot {
  row: string,
  col: number,
  value: number,
}

export interface IWordcloud {
  freq: number,
  word: string,
}

export interface IRidgelineData {
  [key: string]: number[],
}
