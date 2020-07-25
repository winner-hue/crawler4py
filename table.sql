-- auto-generated definition
create table tasks
(
  task_id       char(32)                               not null comment '任务id为任务url的md5值'
    primary key,
  task_url      varchar(500)                           null comment '任务url',
  task_cell     int unsigned default '3600'            null comment '任务时间间隔',
  exec_time     datetime     default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
  pre_exec_time datetime     default CURRENT_TIMESTAMP null,
  task_type     int unsigned                           null comment '任务类型',
  task_status   int unsigned default '0'               null comment '任务状态',
  task_add_time datetime     default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '任务添加时间',
  task_encode   varchar(10)                            null
);