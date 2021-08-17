# OIDC_Analysis_Service (분석 서비스)
심박수 기반 영화 순위 제공서비스 'Movie by Heart'의 분석 서비스를 구성하는 레포지토리

<br>

### 심박수 분석 순위 산출

- Mdata (GET) **/valurate/mda/**

  - db BPMDATA 테이블에 저장되어있는 bpm 중 최댓값, 최솟값을 호출하여 MOVIEINFO 테이블에 BMAX, BMIN에 저장

<br>

- calaver (GET) **/valurate/cal/**

  - DB BPMDATA 테이블의 데이터를 초단위로 불러와 초당 bpm 평균을 계산하여 DB MOVIEGRAPH에 저장

<br>

- cluster (GET) **/valurate/clu/**

  - DB BPMDATA 테이블의 bpm을 클러스터중심점 3개로 클러스터링하고 각 데이터를 중심점과의 거리 비교 후 가장 가까운 군집에 기준에 맞춰 점수 산출. 산출된 점수를 DB SCORING 테이블에 저장

<br>

- rating (GET) **/valurate/rat/**

  - DB SCORING 테이블의 점수와 mid를 불러와서 점수 순위대로 정렬해 MOVIERANK에 저장

<br>

### 협업필터링을 활용한 사용자 맞춤 영화 추천

- recommand (GET) **/valuerate/rec**
  - parameter : uid
  - 사용자의의 UID를 parameter로 받아서 USERINFO의 UAGE(나이)를 획득.
  - 해당 사용자의 연령대 가 유사한 사용자를 찾고 유사 사용자의 시청목록을 중복 제거 한 뒤 랜덤하게 추천
