---
name: kube-rca-chaos
description: |
  Chaos Mesh-based failure injection for the kube-rca project. Use when working on the
  chaos/ directory, scenario manifests, or Makefile targets for OOMKilled, CrashLoopBackOff,
  ImagePullBackOff, or other chaos experiments, including microservices-demo targets.
---

# Kube-RCA Chaos

## Scope

- `chaos/` scripts, scenarios, Makefile, and README
- Chaos Mesh manifests (`StressChaos`, `PodChaos`, etc.)
- Failure injection workflows and cleanup behavior
- Demo application targeting for microservices-demo deployments

## Workflow

1. Review `chaos/Makefile` and `chaos/scripts/run_scenario.sh`.
2. Add or update scenario manifests under `chaos/scenarios/<scenario>/`.
3. Ensure each scenario:
   - Applies the target workload
   - Optionally applies Chaos Mesh manifests
   - Waits for the expected failure reason
   - Cleans up on Enter or Ctrl+C
4. Update `chaos/README.md` and Makefile targets.
5. Keep agent analyze helpers under `chaos/scripts/agent/` and update `agent/Makefile` if paths change.

## Demo Application (microservices-demo)

- Repository: `https://github.com/GoogleCloudPlatform/microservices-demo.git`
- Deployment details (namespace, service names, labels) must be verified from the
  upstream README and the actual cluster state after deployment.
- Discover label selectors before authoring Chaos Mesh manifests:
  - `kubectl -n <namespace> get deploy <name> -o jsonpath='{.spec.selector.matchLabels}'`
  - `kubectl -n <namespace> get deploy --show-labels`
- When targeting microservices-demo, use its real labels in Chaos Mesh selectors
  instead of the local `app=chaos-<scenario>-target` convention.

## Conventions

- Label selector: `app=chaos-<scenario>-target`
- Target manifest: `target-deployment.yaml`
- Chaos Mesh manifest: `stress-chaos.yaml` or `pod-chaos.yaml`
- Avoid secrets in manifests

## Verification

- `bash -n chaos/scripts/run_scenario.sh`
