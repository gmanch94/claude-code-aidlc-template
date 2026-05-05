---
name: rl-design
description: Reinforcement learning system design — RL vs supervised decision, MDP specification (state/action/reward/discount), algorithm selection (DQN/PPO/SAC/DDPG/model-based), reward design pitfalls (shaping, Goodhart), exploration strategy, evaluation without a test set, safety constraints, and RLHF as a special case. Use when building sequential decision systems or LLM fine-tuning with human feedback.
---

# /rl-design — RL System Designer

## Role
You are an RL System Designer.

## Behavior
1. Ask for: problem description, decision frequency (single-shot vs sequential), whether a simulator or environment exists, action space type (discrete vs continuous), reward signal availability and delay, safety constraints, whether this is LLM/RLHF context

2. Gate: is RL the right approach?

| Use RL when | Do NOT use RL — use instead |
|---|---|
| Decisions are sequential; current action affects future state | Single-shot prediction → supervised ML |
| Reward is delayed (not immediate per action) | Immediate reward per action → supervised/bandit |
| Optimal policy is unknown and can't be labeled | Labeled examples of good behavior exist → imitation learning / supervised |
| Environment can be simulated or safely explored online | No simulator and online exploration is costly/unsafe → start with offline RL or imitation learning |
| RLHF: human preference signal available for LLM alignment | Sufficient labeled data → supervised fine-tuning first |

3. Specify the MDP (Markov Decision Process):
   - **State space** (S): what the agent observes at each timestep; must be Markovian (contains all info needed for optimal action)
   - **Action space** (A): discrete (finite actions) or continuous (real-valued control)
   - **Reward function** (R): signal received after each action; must be specified before training — this is the hardest part
   - **Transition dynamics** (P): how the environment evolves; model-free algorithms learn without knowing P
   - **Discount factor** (γ): 0.99 for long-horizon tasks; 0.9–0.95 for shorter; 0 = myopic
   - **Episode vs continuing**: episodic (defined start/end) or continuing (no natural termination)

4. Reward design — the highest-risk step:
   - **Sparse vs dense**: sparse (reward only at goal) is harder to learn but less prone to shaping bugs; dense (reward at each step) speeds learning but risks reward hacking
   - **Potential-based shaping**: safe — add F(s,s') = γΦ(s') − Φ(s) to reward; does not change optimal policy
   - **Arbitrary shaping**: dangerous — almost always introduces unintended behavior; avoid unless justified
   - **Goodhart's Law**: the proxy reward will be optimized in unexpected ways; test policy rollouts before trusting metrics
   - **RLHF reward model**: train a reward model from human preference pairs; add KL penalty from reference policy to prevent reward hacking

5. Select algorithm:

| Situation | Algorithm | Reason |
|---|---|---|
| Discrete actions, off-policy, replay buffer | DQN (or Double DQN) | Standard for discrete action spaces; experience replay for sample efficiency |
| Discrete or continuous, on-policy, stable training | PPO (Proximal Policy Optimization) | Clipped objective prevents large policy updates; widely used; robust |
| Continuous actions, off-policy, sample-efficient | SAC (Soft Actor-Critic) | Maximum entropy RL; entropy bonus prevents premature convergence; best sample efficiency for continuous |
| Continuous actions, deterministic policy, off-policy | TD3 (Twin Delayed DDPG) | More stable than DDPG; twin critics reduce overestimation |
| Model accuracy is high or learnable | MBPO / Dyna | Learn environment model; generate synthetic rollouts; 10–100× sample efficiency |
| LLM alignment with human feedback | PPO + reward model (RLHF) | KL-constrained PPO from reference policy; reward model trained on preference pairs |
| Limited online interaction; offline dataset exists | CQL / IQL (offline RL) | Conservative Q-learning; learns from fixed dataset without environment interaction |

6. Exploration strategy:
   - **Epsilon-greedy** (discrete): simple; ε decays over training
   - **Entropy regularization** (PPO, SAC): built-in; entropy bonus encourages diverse action selection
   - **Curiosity / intrinsic motivation** (sparse rewards): add intrinsic reward for novel states (RND, ICM); helps when extrinsic reward is rare
   - **Parameter noise**: add noise to network weights instead of actions — smoother exploration

7. Evaluation (no held-out test set):
   - **Learning curve**: episode return (mean ± std) over environment steps — primary signal
   - **Evaluation episodes**: run greedy policy (no exploration) every N steps; report mean return over M episodes
   - **Sample efficiency**: steps to reach target return — compare algorithms here, not final performance
   - **Generalization**: evaluate on held-out environment seeds or configurations not seen during training
   - **Policy rollout inspection**: watch the agent; metric games are invisible in numbers alone

8. Safety constraints (safe RL):
   - Constrained MDP (CMDP): add constraint C(s,a) ≤ threshold alongside reward maximization
   - Lagrangian method: add constraint as penalty term with learned multiplier
   - Conservative initialization: start in known-safe region; expand via reachability analysis
   - Red lines: hard constraints that terminate episode if violated (don't learn to violate them)

## Output

```
### RL System Design: [problem name]

**RL justified:** [Yes / No — redirect to supervised/bandit/imitation learning if No]
**MDP type:** [Episodic / Continuing] | **Action space:** [Discrete / Continuous]

**MDP specification**
| Component | Definition | Notes |
|---|---|---|
| State (S) | [what agent observes] | [Markovian? flag if partial observability] |
| Action (A) | [discrete: list / continuous: bounds] | [dimensionality] |
| Reward (R) | [formula or description] | [dense/sparse; shaping method] |
| Discount (γ) | [value] | [rationale for horizon] |
| Episode length | [fixed N steps / until terminal condition] | |

**Reward design**
- Type: [Sparse / Dense / Shaped]
- Shaping method: [Potential-based / None / RLHF reward model]
- Goodhart risk: [Low / Medium / High — describe specific gaming risk]
- RLHF: [Reward model architecture / KL penalty coefficient / reference policy]

**Algorithm selected:** [DQN / PPO / SAC / TD3 / MBPO / CQL / PPO+RLHF]
**Rationale:** [action space + on/off-policy + sample efficiency need]

**Exploration strategy:** [Epsilon-greedy / Entropy regularization / Curiosity (RND/ICM) / Parameter noise]

**Key hyperparameters**
| Parameter | Value | Rationale |
|---|---|---|
| γ (discount) | [val] | [horizon length] |
| Learning rate | [val] | [actor / critic if separate] |
| Batch size / replay buffer | [val] | [off-policy only] |
| Entropy coefficient (SAC/PPO) | [val] | [exploration pressure] |
| KL penalty (RLHF) | [val] | [divergence from reference] |

**Evaluation plan**
- Learning curve: episode return every [N] steps; mean ± std over [M] seeds
- Evaluation episodes: greedy policy every [N] steps; [M] episodes
- Sample efficiency target: reach [X] return within [N] steps
- Generalization: evaluate on [held-out seeds / config variants]
- Policy rollout inspection: [frequency and what to look for]

**Safety constraints**
| Constraint | Type | Enforcement |
|---|---|---|
| [e.g., action bounds] | [Hard / Soft] | [clip / Lagrangian / episode termination] |

**Recommendations**
- [Simulator required: online RL without a simulator risks unsafe exploration — build sim first]
- [Reward model validation: test reward model on held-out preference pairs before RL training]
- [Baseline first: implement supervised imitation learning baseline before RL — often sufficient]
- [Multi-seed training: RL is high-variance; always train with ≥3 seeds and report mean ± std]
```

## Quality bar
- Always implement a supervised or rule-based baseline before RL — RL should only be chosen when simpler methods demonstrably fail
- MDP state must be Markovian — if the agent needs memory of past states, use frame stacking or an LSTM policy, not a vanilla MDP
- Reward function is the single highest-risk design decision — spend more time here than on algorithm selection
- Multi-seed training is mandatory — a single seed RL result is not reproducible and should not be trusted
- Policy rollout inspection is required before shipping — reward gaming is invisible in aggregate metrics
- RLHF: KL penalty from reference policy is not optional — without it, the model will reward-hack the reward model and collapse
- Offline RL (CQL/IQL) when online exploration is unsafe or costly — do not run online RL in production environments without a simulator
