<h1 align="center">Heave-Ho: Decentralized Long-Horizon<br>Multi-Humanoid Collaboration</h1>

<p align="center">
  <a href="https://koi953215.github.io/">Ting-Hsuan Chen</a><sup>1*</sup>&nbsp;&nbsp;
  <a href="https://sihengz02.github.io/">Siheng Zhao</a><sup>1*&Dagger;</sup>&nbsp;&nbsp;
  <a href="https://hanjiang.site/">Han Jiang</a><sup>1*</sup>&nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/qi-pan-179050384/">Qi Pan</a><sup>1</sup>&nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/louisonlu/">Louison Lu</a><sup>1</sup>
  <br>
  <a href="https://kb-jiaheng.github.io/about/">Jiaheng Luo</a><sup>1</sup>&nbsp;&nbsp;
  <a href="https://henghuib.github.io/">Henghui Bao</a><sup>1</sup>&nbsp;&nbsp;
  <a href="https://openreview.net/profile?id=%7EYiyu_Chen4">Yiyu Chen</a><sup>2</sup>&nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/qtn/">Quan Nguyen</a><sup>1</sup>&nbsp;&nbsp;
  <a href="https://yuewang.xyz/">Yue Wang</a><sup>1&dagger;</sup>
</p>

<p align="center">
  <sup>1</sup>University of Southern California&nbsp;&nbsp;&nbsp;<sup>2</sup>VinMotion
  <br>
  <sup>*</sup>Equal contribution&nbsp;&nbsp;&nbsp;<sup>&dagger;</sup>Corresponding author&nbsp;&nbsp;&nbsp;<sup>&Dagger;</sup>Project lead
</p>

<p align="center">
  <a href="https://heaveho-humanoid.github.io/"><img src="https://img.shields.io/badge/Project-Page-2f6db5?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Project Page"></a>
  <img src="https://img.shields.io/badge/arXiv-coming%20soon-b31b1b?style=for-the-badge&logo=arxiv&logoColor=white" alt="arXiv (coming soon)">
  <img src="https://img.shields.io/badge/Code-coming%20Dec%202026-18202c?style=for-the-badge&logo=github&logoColor=white" alt="Code (coming by the end of December 2026)">
</p>

<p align="center">
  <img src="assets/teaser.jpg" width="100%" alt="Heave-Ho teaser">
</p>

> [!NOTE]
> **Code release:** we plan to release the code by the end of December 2026. Watch or star this repository to get notified.
> In the meantime, videos of all real-world and simulated experiments are on the [project page](https://heaveho-humanoid.github.io/).

## Abstract

Collaboration promises to extend humanoid capabilities beyond what individual robots can achieve. However, realizing this potential requires coordinated whole-body interactions, coherent long-horizon planning, and precise synchronization across robots. We introduce **Heave-Ho**, a decentralized framework for long-horizon collaborative multi-humanoid loco-manipulation. At the low level, we develop a multi-agent post-training framework that adapts a humanoid foundation tracking model to physically coupled interactions between humanoids, enabling coordinated decentralized control from local observations alone. At the high level, we train a vision-language planner and design a speech-based leader-follower coordination mechanism to synchronize decentralized execution without network communication. Trained with two identical humanoids, our system scales to teams of up to ten robots and generalizes to heterogeneous teams without retraining. To benchmark these capabilities, we introduce **HH-Bench**, comprising 12 tasks involving teams of 2 to 10 humanoids, including heterogeneous teams. Systematic evaluations show that Heave-Ho consistently outperforms baseline methods, while real-world experiments demonstrate robust decentralized collaboration across challenging tasks.

## Overview

<p align="center">
  <img src="assets/overview.jpg" width="100%" alt="Heave-Ho overview">
</p>

At the high level, the leader's vision-language planner selects the next team skill from its camera and speaks it; every follower recognizes the command on board, and all robots start it on a shared skill schedule. At the low level, each robot maps the team skill to its own role, generates a reference conditioned on the object specification, and tracks it with a frozen foundation tracking model plus a residual policy shared by all robots. No network message is exchanged between robots.

## Citation

A BibTeX entry will be added here once the paper is on arXiv.
