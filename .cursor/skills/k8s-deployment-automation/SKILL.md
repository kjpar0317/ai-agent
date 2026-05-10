---
name: k8s-deployment-automation
description: Kubernetes(k8s) 배포 자동화를 안내한다. 매니페스트, Helm/Kustomize, CI/CD 파이프라인, GitOps(Argo CD, Flux), 롤아웃, 헬스 프로브, 리소스 한도, 시크릿을 다룬다. 사용자가 k8s, Kubernetes, 배포, deployment, Helm, GitOps, 클러스터 롤아웃 자동화를 언급할 때 사용한다.
disable-model-invocation: true
app-runtime: false
---

# Kubernetes 배포 자동화

## 지침

k8s 배포 자동화를 도울 때, 아직 불명확하면 먼저 **대상**을 정리한다: 클러스터 접근 방식, 환경(dev/stage/prod), 조직이 **푸시**(CI가 매니페스트 적용)인지 **GitOps**(컨트롤러가 git과 동기화)인지.

### 기본 가정

- 반복 가능한 작업은 임시 `kubectl run`류보다 **선언적** 설정(git의 YAML)을 우선한다.
- **패키징/구조**: 단일 앱 → 환경별 Helm 차트 또는 Kustomize 오버레이; 다수 앱 → umbrella 차트 또는 공유 base가 있는 저장소 레이아웃.
- **적용 순서**: 네임스페이스·CRD(있으면) → RBAC → 워크로드 → 의존성이 없으면 Ingress/네트워크 정책은 후순위.

### CI/CD(푸시 모델)

1. 이미지 빌드 후 **불변 태그**로 푸시(다이제스트 또는 `git sha`; 운영은 `latest` 지양).
2. 매니페스트의 이미지 참조 갱신(Helm `values`, Kustomize `images`, 또는 패치).
3. `kubectl apply` / `helm upgrade`는 **비대화형** 플래그와, CI 시크릿의 kubecontext 또는 kubeconfig를 명시한다.
4. 롤아웃 대기: `kubectl rollout status deployment/<이름> -n <ns> --timeout=...`
5. 실패 시: 실패 워크로드에 대해 `kubectl describe` / `kubectl logs`로 원인을 드러낸다.

### GitOps(풀 모델)

- **Argo CD**: Application CR이 저장소 경로를 가리킨다. 동기 정책(수동 vs 자동). 순서는 헬스 체크·sync wave를 활용한다.
- **Flux**: Kustomization/HelmRelease에 `dependsOn`으로 순서를 맞춘다. 환경에 맞는 reconcile 간격을 둔다.
- 앱 저장소에 cluster-admin kubeconfig를 넣지 않는다. 가능하면 네임스페이스 단위로 SA 권한을 제한한다.

### 매니페스트 품질 체크리스트

- **프로브**: `readinessProbe`는 실제 의존성과 맞춘다. 느린 콜드 스타트에서 동일한 `liveness`로 죽이지 않도록 주의한다.
- **리소스**: requests·limits를 둔 뒤 HPA/VPA를 검토한다.
- **보안**: non-root, 가능하면 `readOnlyRootFilesystem`, capability 축소, 평문 YAML에 시크릿 값 금지(External Secrets, Sealed Secrets, 클라우드 secret CSI 등 팀 표준 사용).
- **가용성**: 제거(eviction) 제어가 필요하면 PDB; replica > 1이면 topology spread 또는 anti-affinity 검토.

### 롤아웃과 롤백

- **Deployment**의 `maxUnavailable` / `maxSurge`는 SLO에 맞게 조정한다. 안정적 아이덴티티/스토리지는 **StatefulSet**.
- 롤백: `kubectl rollout undo` 또는 Git revert + GitOps 동기화. 팀에서 **정본(canonical)**이 무엇인지 문서화한다.

### 출력 기대

- **복사·붙여넣기 가능한** 명령을 주고, 자리 표시자는 `<namespace>`, `<release>` 형태로 둔다.
- GitHub Actions·GitLab CI 등 워크플로 YAML을 제안할 때 해당 단계에 필요한 **시크릿·권한**(레지스트리 로그인, kubeconfig 또는 클라우드 OIDC)을 함께 적는다.
- 저장소에 이미 있는 도구(Helm vs Kustomize vs 순수 YAML)에 맞추고, 두 번째 패키징 방식을 함부로 도입하지 않는다.

## 예시

**CI에서 Helm 업그레이드**

```bash
helm upgrade --install myapp ./chart -n apps --create-namespace \
  -f values.prod.yaml \
  --set image.tag="${GITHUB_SHA}" \
  --atomic --wait --timeout 10m
```

**롤아웃 확인**

```bash
kubectl rollout status deployment/myapp -n apps --timeout=5m
kubectl get pods -n apps -l app=myapp
```

## 추가 자료

- GitOps 패턴·CR 예시는 [reference.md](reference.md)를 본다.
