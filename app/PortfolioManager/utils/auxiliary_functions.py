from app.repository.portfolio import RepositoryPortfolio
from app.infra.config.database import get_db_session


def repository_portfolio_manage():
    """Cria uma instância do repositório com sessão gerenciada."""
    with get_db_session() as session:
        return RepositoryPortfolio(session=session)
