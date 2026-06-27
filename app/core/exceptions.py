"""도메인 공통 예외 클래스."""


class EntityNotFoundError(Exception):
    """요청한 엔티티(종목·데이터)가 존재하지 않을 때 발생합니다."""

    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} not found: {identifier!r}")
