a simple shell written in python

原项目为：https://github.com/supasate/yosh

Xshell对原项目进行了重构（面向对象）和扩展（支持重定向，管道，&） 

##
支持Python版本：2.7 3.5以上 
主要使用python标准库，不需要其他依赖

##
支持功能： 
（1）shell基本命令
（3）内置命令 
支持history,cd,getenv,exit四条内置命令
（2）重定向 
（3）管道 
（4）&后台启动 

##
存在的问题： 
管道，&后台启动指令显示存在格式上的问题 
内置的exit指令可能会导致bug，原因暂时不明

##
学习要点： 
（1）Python标准库常用模块sys,os,subprocess等的使用 
（2）shell的原理 
（3）重定向，管道的原理
