# env-audit

앱을 실행하거나 배포하기 전에 `.env.example`과 `.env`를 비교해 설정 누락을 찾아주는 CLI입니다. Python 3.10 이상에서 실행하며 외부 실행 의존성이 없습니다.

## 실행

```sh
python env_audit.py --template examples/.env.example --env-file examples/valid.env
python env_audit.py --template examples/.env.example --env-file examples/invalid.env
```

두 번째 명령은 의도적으로 오류를 보고하고 종료 코드 1을 반환합니다.

본인 프로젝트에서는 파일 경로를 지정하거나, `env_audit.py`를 복사한 뒤 아래처럼 실행하세요.

```sh
python env_audit.py
python env_audit.py --strict
python env_audit.py --allow-empty OPTIONAL_KEY --format json
```

- 템플릿의 모든 키를 필수로 취급합니다. 템플릿 값은 기본값으로 쓰이지 않습니다.
- 누락 키, 빈 값, 중복 키, 잘못된 구문을 검사합니다.
- `--strict`는 템플릿에 없는 추가 키도 오류로 처리합니다.
- `--allow-empty KEY`는 해당 키의 빈 값을 허용하며 반복 지정할 수 있습니다. 키 자체의 누락은 허용하지 않습니다.
- 종료 코드는 정상 0, 설정 오류 1, 입력 파일/명령 사용 오류 2입니다.
- 값은 출력하지 않지만 키 이름과 줄 번호는 출력합니다.

단일 줄 dotenv 구문만 지원합니다. 여러 줄 값, 변수 치환, 자료형 검사, 실제 인증 정보의 유효성 검사는 지원하지 않습니다. `changeme` 같은 임시 값도 검출하지 않습니다. 실제 비밀값이 든 파일은 저장소에 올리지 마세요.

## 테스트와 공개

```sh
python -m unittest discover -s tests -v
```

MIT 라이선스, 테스트, GitHub Actions 설정이 포함되어 있습니다. 이 폴더의 내용을 새 GitHub 저장소에 올릴 수 있습니다. GitHub 업로드와 PyPI 배포는 별도로 진행해야 합니다. 자세한 구문과 CI 사용법은 [영문 문서](README.md)를 참고하세요.
