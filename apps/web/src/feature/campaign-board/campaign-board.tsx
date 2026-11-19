import { Stack } from '@/ui';
import { useCampaignBoard } from './use-campaign-board';
import styles from './campaign-board.module.css';

/** Stored campaigns and the control that syncs them. */
export function CampaignBoard() {
  const board = useCampaignBoard();

  return (
    <Stack as="section" variant="start">
      {board.isLoading ? <p className="muted">Загрузка…</p> : null}

      {board.isError ? <p className="status">Не удалось загрузить кампании.</p> : null}

      {!board.isLoading && !board.isError && board.campaigns.length === 0 ? (
        <p>Кампаний пока нет.</p>
      ) : null}

      {board.campaigns.length > 0 ? (
        <ul className={styles.rows}>
          {board.campaigns.map((campaign) => (
            <li key={campaign.id}>{campaign.label}</li>
          ))}
        </ul>
      ) : null}

      <button type="button" onClick={board.sync} disabled={board.syncing}>
        Синхронизировать
      </button>

      {board.syncFailed ? <p className="status">Не удалось синхронизировать.</p> : null}
    </Stack>
  );
}
