# k8s 배포 자동화 — 참고

## Argo CD(요약)

- `Application`: `spec.source.repoURL`, `path`, `targetRevision`; `spec.destination.namespace`와 `server` 또는 `name`.
- 동기 옵션 `prune`, `selfHeal` — 영향 범위를 팀이 이해한 뒤에만 켠다.
- Helm 어노테이션·리소스 훅으로 pre/post 동기; 순서는 sync wave(`argocd.argoproj.io/sync-wave`)로 맞춘다.

## Flux(요약)

- `GitRepository` / `OCIRepository` → 경로를 가리키는 `Kustomization`; 필요 시 커스텀 리소스용 `healthChecks`.
- 차트 설치는 `HelmRelease`; Kustomization/릴리스 간 엄격한 순서는 `dependsOn`.

## CI에서 클러스터 인증(패턴)

- GitHub/GitLab에서 클라우드 OIDC → 짧은 수명의 kube 자격(장수 kubeconfig보다 권장).
- kubeconfig가 불가피하면: CI 시크릿, 최소 RBAC, 환경별 분리, 로테이션 절차를 문서화한다.

## 자주 쓰는 장애 분류

1. `kubectl get events -n <ns> --sort-by='.lastTimestamp'`
2. 스케줄링·이미지 풀·마운트 오류: `kubectl describe pod <pod> -n <ns>`
3. 크래시 루프 후: `kubectl logs <pod> -n <ns> --previous`
