/**
 * Six research papers from the author-provided cv.tex (IET book excluded).
 * Author order, contribution marks, submission venues and Spotlight status follow the CV.
 * method: original paper mechanism figure; montage: one simultaneous demo composite.
 * media: archived source inputs for regenerating the composite; not rendered as slides.
 * preview is a legacy single-image fallback. Local paths use ./assets/.
 * Abstract fields reproduce original author-source abstracts with typesetting normalized.
 * Short summary fields are editorial descriptions.
 * Original public videos are preserved; additional author-provided project clips are
 * explicitly documented in public/assets/publications/gallery-sources.json.
 * Video posters are decoded frames; no synthetic diagrams or generated research imagery.
 * Other optional fields: authorLimit, location, note, additional_info, award, badges,
 * venueUrl, pdf/code/website/video/blog/html/poster/slides/supp/doi/arxiv/hal, bibtex.
 * Paper metadata updated 2026-10-16. Acceptance labels are author-provided CV facts;
 * a submission is clearly labeled as such and never presented as an acceptance.
 */
export const publications = [
  {
    "selected": true,
    "year": 2026,
    "annotation": "† Advising.",
    "id": "he2026mga",
    "abbr": "MGA",
    "title": "Manifold Generative Annealing for Contact Constraint-aware Impedance Control with Reinforcement Learning Prior",
    "authors": [
      {
        "name": "Zhilin He",
        "self": true
      },
      {
        "name": "Guoquan Qi"
      },
      {
        "name": "Changliu Liu",
        "annotation": "†"
      }
    ],
    "month": 10,
    "journal": "In submission · ICLR 2027",
    "tags": [
      "Contact-rich manipulation",
      "Impedance control",
      "Reinforcement learning",
      "Generative optimization"
    ],
    "summary": "Learned interaction strategies meet online geometric refinement for surface scanning, peg insertion, and humanoid contact control.",
    "abstract": "Contact-rich robotic tasks require coordinated motion and impedance under uncertain interaction dynamics and physical constraints. While recent methods on learned policies provide useful interaction strategies, they may fail when contact conditions differ from those encountered during training. Model-based generative methods show promising receding-horizon trajectories optimization results, but often lack structured behavioral guidance and refinement that jointly accounts for constraint geometry and actual contact responses. To this end, we propose Manifold Generative Annealing (MGA), a joint model-free and model-based generative framework for motion–impedance optimization. MGA first organizes pretrained reinforcement learning policies into structured sequence proposals, retaining task-specific interaction strategies without committing to their execution. It then evaluates these proposals alongside exploratory samples through model-based rollouts for refinement or separate execution selection. Crucially, realization-aware manifold refinement aligns updates from the refinement bank with both task constraints and locally achievable physical responses, allowing learned experience to guide online adaptation under changing contact conditions. Experiments cover surface scanning, peg insertion, and humanoid pushing, with improved safety success rate of impedance control under nominal and sensing-shift conditions.",
    "arxiv": "2610.21140",
    "pdf": "https://arxiv.org/pdf/2610.21140",
    "html": "https://arxiv.org/html/2610.21140v1",
    "code": "https://github.com/hhhhzl/genedynamics",
    "website": "https://hhhhzl.github.io/generative-dynamics/research/mga/",
    "doi": "10.48550/arXiv.2610.21140",
    "primaryClass": "cs.RO",
    "media": [
      {
        "type": "video",
        "src": "./assets/publications/gallery/hardware_mga_surface_foam.mp4",
        "alt": "Hardware · MGA: compliant scanning",
        "caption": "Hardware · MGA: compliant scanning",
        "poster": "./assets/publications/gallery/hardware_mga_surface_foam.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/hardware_mga_peg_insert.mp4",
        "alt": "Hardware · MGA: peg-insertion hardware",
        "caption": "Hardware · MGA: peg-insertion hardware",
        "poster": "./assets/publications/gallery/hardware_mga_peg_insert.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/hardware_mga_surface_curved.mp4",
        "alt": "Hardware · MGA: curved scanning",
        "caption": "Hardware · MGA: curved scanning",
        "poster": "./assets/publications/gallery/hardware_mga_surface_curved.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mga_surface_hybrid_stripes.mp4",
        "alt": "Simulation · Hybrid: stripes",
        "caption": "Simulation · Hybrid: stripes",
        "poster": "./assets/publications/gallery/mga_surface_hybrid_stripes.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mga_surface_soft_unseen.mp4",
        "alt": "Simulation · Compliant: unseen geometry",
        "caption": "Simulation · Compliant: unseen geometry",
        "poster": "./assets/publications/gallery/mga_surface_soft_unseen.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mga_peg_id_wide.mp4",
        "alt": "Simulation · Peg insertion: wide clearance",
        "caption": "Simulation · Peg insertion: wide clearance",
        "poster": "./assets/publications/gallery/mga_peg_id_wide.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mga_peg_ood_sensing.mp4",
        "alt": "Simulation · Peg insertion: sensing shift",
        "caption": "Simulation · Peg insertion: sensing shift",
        "poster": "./assets/publications/gallery/mga_peg_ood_sensing.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mga_humanoid_fixed_stance_push.mp4",
        "alt": "Simulation · Humanoid: fixed-stance pushing",
        "caption": "Simulation · Humanoid: fixed-stance pushing",
        "poster": "./assets/publications/gallery/mga_humanoid_fixed_stance_push.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mga_humanoid_unjamming.mp4",
        "alt": "Simulation · Humanoid: unjamming",
        "caption": "Simulation · Humanoid: unjamming",
        "poster": "./assets/publications/gallery/mga_humanoid_unjamming.jpg"
      }
    ],
    "preview": {
      "type": "video",
      "src": "./assets/publications/gallery/hardware_mga_surface_foam.mp4",
      "alt": "Hardware · MGA: compliant scanning",
      "caption": "Hardware · MGA: compliant scanning",
      "poster": "./assets/publications/gallery/hardware_mga_surface_foam.jpg"
    },
    "monogram": {
      "label": "MGA",
      "theme": "blue"
    },
    "bibtex": "@misc{he2026mga,\n  title = {Manifold Generative Annealing for Contact Constraint-aware Impedance Control with Reinforcement Learning Prior},\n  author = {Zhilin He and Guoquan Qi and Changliu Liu},\n  year = {2026},\n  note = {In submission · ICLR 2027},\n  eprint = {2610.21140},\n  archivePrefix = {arXiv},\n  primaryClass = {cs.RO},\n  doi = {10.48550/arXiv.2610.21140},\n  url = {https://arxiv.org/abs/2610.21140}\n}",
    "method": {
      "type": "image",
      "src": "./assets/publications/methods/mga.png",
      "alt": "The original MGA framework diagram connects offline training, a learned proposal prior, manifold-aware model-based refinement, and force-adaptive control; four toy-path panels illustrate the role of LRC.",
      "caption": "MGA overview: offline policy training, model-based refinement, and force-adaptive deployment with feedback.",
      "width": 2299,
      "height": 885
    },
    "montage": {
      "type": "video",
      "src": "./assets/publications/gallery/mga-experiments.mp4",
      "gif": "./assets/publications/gallery/mga-experiments.gif",
      "poster": "./assets/publications/gallery/mga-experiments.jpg",
      "width": 1200,
      "height": 900,
      "alt": "MGA: 9 experiment clips shown simultaneously in one animated montage.",
      "caption": "All 9 experiment clips shown together. Each panel loops independently.",
      "sourceCount": 9
    }
  },
  {
    "selected": true,
    "year": 2026,
    "annotation": "† Advising.",
    "id": "he2026twogo",
    "abbr": "2GO",
    "title": "Model-Based Geometry-Aware Generative Optimization for Constrained Locomotion Planning",
    "authors": [
      {
        "name": "Zhilin He",
        "self": true
      },
      {
        "name": "Xinyuan Wang"
      },
      {
        "name": "Changliu Liu",
        "annotation": "†"
      }
    ],
    "month": 10,
    "journal": "In submission · RA-L 2026",
    "tags": [
      "Locomotion",
      "Constraint geometry",
      "Humanoid robotics",
      "Quadrupeds"
    ],
    "summary": "Constraint geometry shapes generative planning for quadruped footholds and humanoid posture in narrow, obstacle-rich environments.",
    "abstract": "Constrained Locomotion Planning (CLP) for quadrupeds and humanoids, where robots must satisfy collision avoidance, contact consistency, kinematic feasibility, and support constraints, is challenging under high-dimensional dynamics and highly non-convex environments. Recent Model-Based Diffusion (MBD) approaches recast trajectory optimization as posterior sampling over trajectories, using known dynamics and Monte Carlo rollouts to analytically estimate the denoising score function without demonstration learning. While constrained variants further incorporate feasibility into model-based score rollouts and show promising performance, they are still limited by (1) lacking a task-modulated active constraint geometry that shapes the score direction and reverse stochasticity, and (2) using deterministic DDPM-style reverse transport without adaptive scheduling across different generative transports. Therefore, we introduce Model-Based Geometry-Aware Generative Optimization (2GO) for constrained locomotion, which turns active constraint geometry into executable denoising operators through normal- induced metric shaping, tangent-space stochastic filtering, and CFS-based retraction. 2GO further decouples generative transport from reverse stochasticity through an adaptive diffusion and flow-like schedule. Experiments on constrained quadruped and humanoid locomotion demonstrate strong performance in discrete foothold selection and continuous posture planning, with higher success rates, fewer violations, and improved execution compatibility. Code: https://github.com/hhhhzl/genedynamics",
    "arxiv": "2610.07772",
    "pdf": "https://arxiv.org/pdf/2610.07772",
    "html": "https://arxiv.org/html/2610.07772v1",
    "code": "https://github.com/hhhhzl/genedynamics",
    "website": "https://hhhhzl.github.io/generative-dynamics/research/2go/",
    "doi": "10.48550/arXiv.2610.07772",
    "primaryClass": "cs.RO",
    "media": [
      {
        "type": "video",
        "src": "./assets/publications/gallery/hardware_twogo_g1.mp4",
        "alt": "Hardware · 2GO: G1 hardware",
        "caption": "Hardware · 2GO: G1 hardware",
        "poster": "./assets/publications/gallery/hardware_twogo_g1.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/twogo_go2_s2.mp4",
        "alt": "Simulation · Go2 stepping stones: S2",
        "caption": "Simulation · Go2 stepping stones: S2",
        "poster": "./assets/publications/gallery/twogo_go2_s2.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/twogo_go2_s1.mp4",
        "alt": "Simulation · Go2 stepping stones: S1",
        "caption": "Simulation · Go2 stepping stones: S1",
        "poster": "./assets/publications/gallery/twogo_go2_s1.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/twogo_g1_zone_a.mp4",
        "alt": "Simulation · G1: central wall (A)",
        "caption": "Simulation · G1: central wall (A)",
        "poster": "./assets/publications/gallery/twogo_g1_zone_a.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/twogo_g1_zone_b.mp4",
        "alt": "Simulation · G1: asymmetric passage (B)",
        "caption": "Simulation · G1: asymmetric passage (B)",
        "poster": "./assets/publications/gallery/twogo_g1_zone_b.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/twogo_g1_zone_c.mp4",
        "alt": "Simulation · G1: tapered squeeze (C)",
        "caption": "Simulation · G1: tapered squeeze (C)",
        "poster": "./assets/publications/gallery/twogo_g1_zone_c.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/twogo_g1_zone_d.mp4",
        "alt": "Simulation · G1: spherical obstacles (D)",
        "caption": "Simulation · G1: spherical obstacles (D)",
        "poster": "./assets/publications/gallery/twogo_g1_zone_d.jpg"
      }
    ],
    "preview": {
      "type": "video",
      "src": "./assets/publications/gallery/hardware_twogo_g1.mp4",
      "alt": "Hardware · 2GO: G1 hardware",
      "caption": "Hardware · 2GO: G1 hardware",
      "poster": "./assets/publications/gallery/hardware_twogo_g1.jpg"
    },
    "monogram": {
      "label": "2GO",
      "theme": "blue"
    },
    "bibtex": "@misc{he2026twogo,\n  title = {Model-Based Geometry-Aware Generative Optimization for Constrained Locomotion Planning},\n  author = {Zhilin He and Xinyuan Wang and Changliu Liu},\n  year = {2026},\n  note = {In submission · RA-L 2026},\n  eprint = {2610.07772},\n  archivePrefix = {arXiv},\n  primaryClass = {cs.RO},\n  doi = {10.48550/arXiv.2610.07772},\n  url = {https://arxiv.org/abs/2610.07772}\n}",
    "method": {
      "type": "image",
      "src": "./assets/publications/methods/twogo.png",
      "alt": "Original 2GO framework diagram showing task modulation, constraint geometry, geometric-aware generative updates, optional CFS correction, and governor-based deployment.",
      "caption": "2GO overview: transport selection, geometry-shaped score and exploration, CFS retraction, and deployment through a reference governor.",
      "width": 2368,
      "height": 933
    },
    "montage": {
      "type": "video",
      "src": "./assets/publications/gallery/2go-experiments.mp4",
      "gif": "./assets/publications/gallery/2go-experiments.gif",
      "poster": "./assets/publications/gallery/2go-experiments.jpg",
      "width": 1200,
      "height": 900,
      "alt": "2GO: 7 experiment clips shown simultaneously in one animated montage.",
      "caption": "All 7 experiment clips shown together. Each panel loops independently.",
      "sourceCount": 7
    }
  },
  {
    "selected": true,
    "year": 2026,
    "annotation": "† Advising.",
    "id": "he2026fedguide",
    "abbr": "FedGuide",
    "title": "FedGuide: Diffusion-Prior Alignment and Value Baseline Guidance for Heterogeneous Federated Reinforcement Learning",
    "authors": [
      {
        "name": "Zhilin He",
        "self": true
      },
      {
        "name": "Gauri Joshi",
        "annotation": "†"
      }
    ],
    "month": 9,
    "booktitle": "Conference on Robot Learning (CoRL)",
    "award": {
      "label": "Spotlight"
    },
    "tags": [
      "Federated learning",
      "Reinforcement learning",
      "Diffusion"
    ],
    "summary": "Diffusion behavior priors and a return-aware value baseline support collaborative policy learning across heterogeneous clients.",
    "abstract": "Federated Reinforcement Learning (FRL) enables collaborative policy learning across distributed agents with heterogeneous environments. While recent methods based on variance reduction, divergence penalization, and momentum optimization improve FRL under heterogeneous settings, they still primarily synchronize policy or value-network parameters and do not explicitly address distributional mismatch among heterogeneous clients. Therefore, we propose FedGuide, a FRL framework that uses diffusion priors as behavior models to provide personalized data supported distributions for heterogeneous local policy learning. Instead of directly averaging local policies, FedGuide aggregates those diffusion priors through Optimal-Transport Mixture-of-Experts (OT-MoE), preserving heterogeneous behavior modes in distribution space. It further develops a Distribution Correction Estimation (DICE) value baseline to provide low-variance, return-aware guidance for local policy improvement. Experiments across heterogeneous environments show that FedGuide outperforms representative FRL methods in client-average returns, final-round performance, and worst-round robustness, while maintaining stable learning under stronger heterogeneity.",
    "arxiv": "2609.18964",
    "pdf": "https://arxiv.org/pdf/2609.18964",
    "code": "https://github.com/hhhhzl/fedguide",
    "website": "https://hhhhzl.github.io/fedguide-page/",
    "doi": "10.48550/arXiv.2609.18964",
    "primaryClass": "cs.LG",
    "media": [
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_halfcheetah_client1.mp4",
        "alt": "Simulation · HalfCheetah · client 1",
        "caption": "Simulation · HalfCheetah · client 1",
        "poster": "./assets/publications/gallery/fedguide_halfcheetah_client1.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_walker_client4.mp4",
        "alt": "Simulation · Walker2D · client 4",
        "caption": "Simulation · Walker2D · client 4",
        "poster": "./assets/publications/gallery/fedguide_walker_client4.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_hopper_client3.mp4",
        "alt": "Simulation · Hopper · client 3",
        "caption": "Simulation · Hopper · client 3",
        "poster": "./assets/publications/gallery/fedguide_hopper_client3.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_reacher_hard_client7.mp4",
        "alt": "Simulation · Reacher-Hard · client 7",
        "caption": "Simulation · Reacher-Hard · client 7",
        "poster": "./assets/publications/gallery/fedguide_reacher_hard_client7.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_metaworld_client2.mp4",
        "alt": "Simulation · Pick & place · client 2",
        "caption": "Simulation · Pick & place · client 2",
        "poster": "./assets/publications/gallery/fedguide_metaworld_client2.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_metaworld_client3.mp4",
        "alt": "Simulation · Door open · client 3",
        "caption": "Simulation · Door open · client 3",
        "poster": "./assets/publications/gallery/fedguide_metaworld_client3.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_metaworld_client8.mp4",
        "alt": "Simulation · Sweep · client 8",
        "caption": "Simulation · Sweep · client 8",
        "poster": "./assets/publications/gallery/fedguide_metaworld_client8.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/fedguide_metaworld_client9.mp4",
        "alt": "Simulation · Basketball · client 9",
        "caption": "Simulation · Basketball · client 9",
        "poster": "./assets/publications/gallery/fedguide_metaworld_client9.jpg"
      },
      {
        "type": "image",
        "src": "./assets/publications/fedguide.png",
        "alt": "Method overview · diffusion priors and value guidance",
        "caption": "Method overview · diffusion priors and value guidance"
      }
    ],
    "preview": {
      "type": "video",
      "src": "./assets/publications/gallery/fedguide_halfcheetah_client1.mp4",
      "alt": "Simulation · HalfCheetah · client 1",
      "caption": "Simulation · HalfCheetah · client 1",
      "poster": "./assets/publications/gallery/fedguide_halfcheetah_client1.jpg"
    },
    "monogram": {
      "label": "FedGuide",
      "theme": "blue"
    },
    "bibtex": "@inproceedings{he2026fedguide,\n  title = {FedGuide: Diffusion-Prior Alignment and Value Baseline Guidance for Heterogeneous Federated Reinforcement Learning},\n  author = {Zhilin He and Gauri Joshi},\n  year = {2026},\n  booktitle = {Conference on Robot Learning (CoRL)},\n  eprint = {2609.18964},\n  archivePrefix = {arXiv},\n  primaryClass = {cs.LG},\n  doi = {10.48550/arXiv.2609.18964},\n  url = {https://arxiv.org/abs/2609.18964},\n  note = {Spotlight presentation}\n}",
    "method": {
      "type": "image",
      "src": "./assets/publications/methods/fedguide.png",
      "alt": "Three original FedGuide panels compare policy-based aggregation, diffusion priors only, and priors with a value baseline in a two-client heterogeneous setting.",
      "caption": "FedGuide method visualization: policy aggregation, diffusion priors, and diffusion priors with value-baseline guidance.",
      "width": 2387,
      "height": 746
    },
    "montage": {
      "type": "video",
      "src": "./assets/publications/gallery/fedguide-experiments.mp4",
      "gif": "./assets/publications/gallery/fedguide-experiments.gif",
      "poster": "./assets/publications/gallery/fedguide-experiments.jpg",
      "width": 1200,
      "height": 656,
      "alt": "FedGuide: 8 experiment clips shown simultaneously in one animated montage.",
      "caption": "All 8 experiment clips shown together. Each panel loops independently.",
      "sourceCount": 8
    }
  },
  {
    "selected": true,
    "year": 2026,
    "annotation": "† Advising.",
    "id": "he2026mdcoas",
    "abbr": "MD-COAS",
    "title": "Motion Planning with Model-Based Diffusion via Constraint Optimization and Adaptive Scheduling",
    "authors": [
      {
        "name": "Zhilin He",
        "self": true
      },
      {
        "name": "Bowei Li"
      },
      {
        "name": "Jianlin Dou"
      },
      {
        "name": "Yuner Zhang"
      },
      {
        "name": "Changliu Liu",
        "annotation": "†"
      }
    ],
    "month": 7,
    "booktitle": "IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)",
    "tags": [
      "Motion planning",
      "Optimal control",
      "Constraints",
      "Diffusion"
    ],
    "summary": "Adaptive scheduling combines soft constraint optimization with hard feasibility projection for constrained motion planning.",
    "abstract": "Single-Robot Motion Planning (SRMP) in highly non-convex constrained environments, where robots must satisfy collision-free guarantees, dynamic feasibility, and task-related constraints, is challenging under complex constraints and computational limits. Recent Model-Based Diffusion (MBD) approaches recast the SRMP as trajectory optimization that samples from a posterior over trajectories, using known dynamics, and analytically estimates the score function from rollout samples to guide diffusion denoising toward a low-cost, clean trajectory without demonstration learning. While existing works further adapt MBD to constrained environments and showcase promising performance, they are still limited by (1) enforcing safety either via soft feasibility diffusion priors or hard projection operators, but lack a unified framework to integrate both, and (2) fixing safety enforcement to neglect the changing of diffusion scheduling. Therefore, we introduce Model-Based Diffusion via Constraint Optimization and Adaptive Scheduling (MD-COAS) for SRMP that unifies the inexact Augmented Lagrangian Method (iALM) soft diffusion prior with a Convex Feasible Set (CFS)-based hard projection operator, and adaptively schedules and co-optimizes safety enforcement, along with diffusion scheduling. Experiments demonstrate that our method achieves higher safety & success rates, faster convergence, and lower final costs than baseline planners on randomly generated highly non-convex 2D benchmarks and a 7-DoF robot arm avoidance task.",
    "arxiv": "2607.14455",
    "pdf": "https://arxiv.org/pdf/2607.14455",
    "html": "https://arxiv.org/html/2607.14455v1",
    "code": "https://github.com/hhhhzl/genedynamics",
    "website": "https://hhhhzl.github.io/generative-dynamics/research/md-coas/",
    "doi": "10.48550/arXiv.2607.14455",
    "primaryClass": "cs.RO",
    "media": [
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_7dof_execution.mp4",
        "alt": "Simulation · 7-DoF: arm execution",
        "caption": "Simulation · 7-DoF: arm execution",
        "poster": "./assets/publications/gallery/mdcoas_7dof_execution.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_7dof_diffusion.mp4",
        "alt": "Simulation · 7-DoF: constrained refinement",
        "caption": "Simulation · 7-DoF: constrained refinement",
        "poster": "./assets/publications/gallery/mdcoas_7dof_diffusion.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_7dof_candidates.mp4",
        "alt": "Simulation · 7-DoF: 20 candidates",
        "caption": "Simulation · 7-DoF: 20 candidates",
        "poster": "./assets/publications/gallery/mdcoas_7dof_candidates.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_2d_l6.mp4",
        "alt": "Simulation · Planar L6: constrained refinement",
        "caption": "Simulation · Planar L6: constrained refinement",
        "poster": "./assets/publications/gallery/mdcoas_2d_l6.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_2d_l6_candidates.mp4",
        "alt": "Simulation · Planar L6: 20 candidates",
        "caption": "Simulation · Planar L6: 20 candidates",
        "poster": "./assets/publications/gallery/mdcoas_2d_l6_candidates.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_2d_l10.mp4",
        "alt": "Simulation · Planar L10: constrained refinement",
        "caption": "Simulation · Planar L10: constrained refinement",
        "poster": "./assets/publications/gallery/mdcoas_2d_l10.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdcoas_2d_l10_candidates.mp4",
        "alt": "Simulation · Planar L10: 20 candidates",
        "caption": "Simulation · Planar L10: 20 candidates",
        "poster": "./assets/publications/gallery/mdcoas_2d_l10_candidates.jpg"
      },
      {
        "type": "image",
        "src": "./assets/publications/md-coas.png",
        "alt": "Method overview · constraint optimization and adaptive scheduling",
        "caption": "Method overview · constraint optimization and adaptive scheduling"
      }
    ],
    "preview": {
      "type": "video",
      "src": "./assets/publications/gallery/mdcoas_7dof_execution.mp4",
      "alt": "Simulation · 7-DoF: arm execution",
      "caption": "Simulation · 7-DoF: arm execution",
      "poster": "./assets/publications/gallery/mdcoas_7dof_execution.jpg"
    },
    "monogram": {
      "label": "MD-COAS",
      "theme": "blue"
    },
    "bibtex": "@inproceedings{he2026mdcoas,\n  title = {Motion Planning with Model-Based Diffusion via Constraint Optimization and Adaptive Scheduling},\n  author = {Zhilin He and Bowei Li and Jianlin Dou and Yuner Zhang and Changliu Liu},\n  year = {2026},\n  booktitle = {IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},\n  eprint = {2607.14455},\n  archivePrefix = {arXiv},\n  primaryClass = {cs.RO},\n  doi = {10.48550/arXiv.2607.14455},\n  url = {https://arxiv.org/abs/2607.14455}\n}",
    "method": {
      "type": "image",
      "src": "./assets/publications/methods/mdcoas.png",
      "alt": "Original MD-COAS diagram shows CFS trajectory projection, constraint optimization, adaptive scheduling, and the model-based diffusion schedule.",
      "caption": "MD-COAS overview: constraint optimization and adaptive scheduling coupled to model-based diffusion.",
      "width": 2600,
      "height": 872
    },
    "montage": {
      "type": "video",
      "src": "./assets/publications/gallery/md-coas-experiments.mp4",
      "gif": "./assets/publications/gallery/md-coas-experiments.gif",
      "poster": "./assets/publications/gallery/md-coas-experiments.jpg",
      "width": 1200,
      "height": 840,
      "alt": "MD-COAS: 7 experiment clips shown simultaneously in one animated montage.",
      "caption": "All 7 experiment clips shown together. Each panel loops independently.",
      "sourceCount": 7
    }
  },
  {
    "selected": true,
    "year": 2026,
    "annotation": "† Advising.",
    "id": "he2026mdoc",
    "abbr": "MDOC",
    "title": "Model-Based Diffusion Optimal Control for Multi-Robot Motion Planning",
    "authors": [
      {
        "name": "Zhilin He",
        "self": true
      },
      {
        "name": "Yorai Shaoul"
      },
      {
        "name": "Jiaoyang Li",
        "annotation": "†"
      }
    ],
    "month": 7,
    "booktitle": "Robotics: Science and Systems (RSS)",
    "tags": [
      "Multi-robot systems",
      "Motion planning",
      "Diffusion",
      "Optimal control"
    ],
    "summary": "Known dynamics, safety projections, and conflict-based search extend model-based diffusion planning to coordinated robot teams.",
    "abstract": "Multi-Robot Motion Planning in continuous environments, where robots must generate dynamically feasible, collision-free trajectories, is challenging due to the combinatorial growth of the joint trajectory space and the difficulty of enforcing dynamic feasibility and hard safety constraints. Recent approaches recast trajectory planning as probabilistic inference, sampling from a posterior over trajectories using diffusion models whose score functions are learned from demonstration data. While showing promising performance, these approaches are limited: they often rely on sizable demonstration datasets and struggle to rigorously enforce dynamics and hard safety constraints during sampling. To this end, we introduce Model-Based Diffusion Optimal Control (MDOC), a model-based diffusion planner that efficiently produces dynamically feasible trajectories without relying on data. Crucially, we show that MDOC's safety mechanism—combining known dynamics models with Control Barrier Function-constrained projections—naturally scales to multi-robot planning settings through Conflict-Based Search. Across simulation experiments, this integrated method consistently outperforms representative baseline planners in sample efficiency, geometric smoothness, and success rate, while reducing computation time and producing collision-free trajectories. Code: https://github.com/hhhhzl/mdoc",
    "arxiv": "2607.12423",
    "pdf": "https://arxiv.org/pdf/2607.12423",
    "html": "https://arxiv.org/html/2607.12423v1",
    "code": "https://github.com/hhhhzl/mdoc",
    "website": "https://hhhhzl.github.io/generative-dynamics/research/mdoc/",
    "doi": "10.15607/RSS.2026.XXII.041",
    "primaryClass": "cs.RO",
    "media": [
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdoc_cbs_random.mp4",
        "alt": "Simulation · Random-obstacle coordination",
        "caption": "Simulation · Random-obstacle coordination",
        "poster": "./assets/publications/gallery/mdoc_cbs_random.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdoc_cbs_conveyor_boundary.mp4",
        "alt": "Simulation · Conveyor coordination",
        "caption": "Simulation · Conveyor coordination",
        "poster": "./assets/publications/gallery/mdoc_cbs_conveyor_boundary.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdoc_cbs_dropregion_boundary.mp4",
        "alt": "Simulation · Drop-region coordination",
        "caption": "Simulation · Drop-region coordination",
        "poster": "./assets/publications/gallery/mdoc_cbs_dropregion_boundary.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdoc_cbs_empty_large.mp4",
        "alt": "Simulation · Open-area coordination",
        "caption": "Simulation · Open-area coordination",
        "poster": "./assets/publications/gallery/mdoc_cbs_empty_large.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdoc_single_narrow.mp4",
        "alt": "Simulation · Narrow-passage navigation",
        "caption": "Simulation · Narrow-passage navigation",
        "poster": "./assets/publications/gallery/mdoc_single_narrow.jpg"
      },
      {
        "type": "video",
        "src": "./assets/publications/gallery/mdoc_single_conveyor.mp4",
        "alt": "Simulation · Conveyor navigation",
        "caption": "Simulation · Conveyor navigation",
        "poster": "./assets/publications/gallery/mdoc_single_conveyor.jpg"
      },
      {
        "type": "image",
        "src": "./assets/publications/mdoc.png",
        "alt": "MDOC-CBS · Conveyor experiment",
        "caption": "MDOC-CBS · Conveyor experiment"
      }
    ],
    "preview": {
      "type": "video",
      "src": "./assets/publications/gallery/mdoc_cbs_random.mp4",
      "alt": "Simulation · Random-obstacle coordination",
      "caption": "Simulation · Random-obstacle coordination",
      "poster": "./assets/publications/gallery/mdoc_cbs_random.jpg"
    },
    "monogram": {
      "label": "MDOC",
      "theme": "blue"
    },
    "bibtex": "@inproceedings{he2026mdoc,\n  title = {Model-Based Diffusion Optimal Control for Multi-Robot Motion Planning},\n  author = {Zhilin He and Yorai Shaoul and Jiaoyang Li},\n  year = {2026},\n  booktitle = {Robotics: Science and Systems (RSS)},\n  eprint = {2607.12423},\n  archivePrefix = {arXiv},\n  primaryClass = {cs.RO},\n  doi = {10.15607/RSS.2026.XXII.041},\n  url = {https://arxiv.org/abs/2607.12423}\n}",
    "montage": {
      "type": "video",
      "src": "./assets/publications/gallery/mdoc-experiments.mp4",
      "gif": "./assets/publications/gallery/mdoc-experiments.gif",
      "poster": "./assets/publications/gallery/mdoc-experiments.jpg",
      "width": 1200,
      "height": 856,
      "alt": "MDOC: 6 experiment clips shown simultaneously in one animated montage.",
      "caption": "All 6 experiment clips shown together. Each panel loops independently.",
      "sourceCount": 6
    }
  },
  {
    "id": "wang2024antivirus",
    "abbr": "Antivirus Routing",
    "title": "Optimal Control for Antivirus Routing in Epidemiological-Based Heterogeneous Computer Network Clusters",
    "authors": [
      {
        "name": "Shuangge Wang",
        "annotation": "*"
      },
      {
        "name": "Zhilin He",
        "self": true,
        "annotation": "*"
      },
      {
        "name": "Zihao Xu",
        "annotation": "*"
      },
      {
        "name": "Cymra Haskell",
        "annotation": "†"
      },
      {
        "name": "Bhaskar Krishnamachari",
        "annotation": "†"
      }
    ],
    "year": 2024,
    "selected": true,
    "booktitle": "American Control Conference (ACC)",
    "annotation": "* Equal contribution. † Advising.",
    "tags": [
      "Optimal control",
      "Network systems",
      "Epidemiological models"
    ],
    "summary": "Optimal antivirus routing accounts for heterogeneous network clusters and communication constraints to preserve network productivity.",
    "abstract": "Maintaining productivity in computer networks amidst virus threats has been an ongoing research challenge. Existing studies often use epidemiological-based ordinary differential equations (ODEs) to model virus and antivirus propagation. However, these models typically oversimplify the situation by not accounting for the heterogeneity among different network clusters and ignoring real-world protocol constraints, such as the inability of nodes to communicate simultaneously with nodes in different groups. In this work, we develop a novel model that addresses these limitations by incorporating both heterogeneity and protocol constraints. We start by proposing a single-cluster ODE model where both virus and antivirus propagate. This model is then extended to networks with heterogeneous clusters. Utilizing these models, we formulate the objective of maximizing productivity as an optimization problem solvable through quasi-Newton methods. We also validate the optimal control's effectiveness in the single-cluster model using Pontryagin's Maximum Principle (PMP). Through experimentation and simulation, we discover that the optimal control policy follows a bang-bang structure and effectively prioritizes actions based on the heterogeneity of clusters.",
    "pdf": "https://raw.githubusercontent.com/hhhhzl/sir_antivirus/main/assets/preprint.pdf",
    "html": "https://ieeexplore.ieee.org/document/10644719",
    "code": "https://github.com/hhhhzl/sir_antivirus",
    "media": [
      {
        "type": "image",
        "src": "./assets/publications/gallery/acc_singlecluster_updated.png",
        "alt": "Single-cluster virus and antivirus dynamics",
        "caption": "Single-cluster virus and antivirus dynamics"
      },
      {
        "type": "image",
        "src": "./assets/publications/gallery/acc_multicluster_large.png",
        "alt": "Heterogeneous network cluster model",
        "caption": "Heterogeneous network cluster model"
      },
      {
        "type": "image",
        "src": "./assets/publications/gallery/acc_experiment_results.png",
        "alt": "Optimal antivirus routing: experiment results",
        "caption": "Optimal antivirus routing: experiment results"
      }
    ],
    "bibtex": "@inproceedings{wang2024optimal,\n  title = {Optimal Control for Antivirus Routing in Epidemiological-Based Heterogeneous Computer Network Clusters},\n  author = {Wang, Shuangge and He, Zhilin and Xu, Zihao and Haskell, Cymra and Krishnamachari, Bhaskar},\n  booktitle = {2024 American Control Conference (ACC)},\n  pages = {4624--4630},\n  year = {2024},\n  organization = {IEEE}\n}",
    "preview": {
      "type": "image",
      "src": "./assets/publications/gallery/acc_singlecluster_updated.png",
      "alt": "Single-cluster virus and antivirus dynamics",
      "caption": "Single-cluster virus and antivirus dynamics"
    },
    "monogram": {
      "label": "Antivirus Routing",
      "theme": "blue"
    },
    "method": {
      "type": "image",
      "src": "./assets/publications/methods/acc.png",
      "alt": "Original three-cluster model showing susceptible, infected and recovered states, intra-cluster migration, and antivirus communication between clusters.",
      "caption": "Heterogeneous-cluster system model: antivirus communication and node-state transitions across three network clusters.",
      "width": 2018,
      "height": 922
    }
  }
];

const bibEscape = (value) => String(value).replace(/[{}]/g, '').replace(/&/g, '\\&');

/** Preserve supplied BibTeX; otherwise build a factual arXiv citation. */
export function publicationBibTeX(paper) {
  if (typeof paper.bibtex === 'string' && paper.bibtex.trim()) return paper.bibtex.trim();
  const arxiv = typeof paper.arxiv === 'string' && !paper.arxiv.includes('/') ? paper.arxiv : '';
  const fields = [
    ['title', `{${bibEscape(paper.title)}}`],
    ['author', paper.authors.map((author) => bibEscape(typeof author === 'string' ? author : author.name)).join(' and ')],
    ['year', paper.year],
    ...(paper.booktitle ? [['booktitle', paper.booktitle]] : []),
    ...(paper.school ? [['school', paper.school]] : []),
    ...(paper.journal && paper.journal !== 'arXiv preprint' ? [['journal', paper.journal]] : []),
    ...(arxiv ? [['eprint', arxiv], ['archivePrefix', 'arXiv']] : []),
    ...(paper.primaryClass ? [['primaryClass', paper.primaryClass]] : []),
    ...(typeof paper.doi === 'string' ? [['doi', paper.doi.replace(/^https?:\/\/doi\.org\//, '')]] : []),
    ...(arxiv ? [['url', `https://arxiv.org/abs/${arxiv}`]] : []),
  ];
  return `@misc{${paper.id},\n${fields.map(([key, value]) => `  ${key} = {${value}}`).join(',\n')}\n}`;
}

export const allBibTeX = publications.map(publicationBibTeX).join('\n\n') + '\n';
