export interface IPush {
  push_content: string,
  push_ipdatetime: string,
  push_tag: string,
  push_userid: string,
}

export interface IPost {
  article_id: string,
  article_title: string,
  author_id: string,
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
