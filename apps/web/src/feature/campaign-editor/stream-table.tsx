import type { FormEvent } from 'react';
import type { StreamRowVm } from '@/view-models';
import styles from './campaign-editor.module.css';

type StreamTableProps = {
  /** Rows in display order. Empty before the first fetch. */
  readonly rows: readonly StreamRowVm[];

  /** Archives one live binding. */
  readonly onRemove: (bindingId: number) => void;

  /** Restores one deleted binding. */
  readonly onBringBack: (bindingId: number) => void;

  /** Fixes one offer at this share. */
  readonly onPin: (bindingId: number, share: string) => void;

  /** Returns one offer to the split. */
  readonly onUnpin: (bindingId: number) => void;

  /** Writes the stream's active offers to Keitaro. */
  readonly onPush: (streamId: number) => void;

  /** Drops unpublished bindings and restores the snapshot. */
  readonly onCancel: (streamId: number) => void;
};

/** Flows, shares, and the actions for one campaign. */
export function StreamTable({
  rows,
  onRemove,
  onBringBack,
  onPin,
  onUnpin,
  onPush,
  onCancel,
}: StreamTableProps) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Flow</th>
          <th>Share</th>
          <th>Stats</th>
          <th>Trends</th>
          <th>Action</th>
        </tr>
      </thead>

      <tbody>
        {rows.map((row) => (
          <tr key={row.key} className={rowClass(row)}>
            <td>{row.flow}</td>
            <td>
              {row.header ? '' : row.share}

              {row.pin ? (
                <form className={styles.actions} onSubmit={(event) => submitPin(event, row.bindingId, onPin)}>
                  <input name="share" key={`${row.bindingId}-${row.share}`} defaultValue={row.share} />
                  <button type="submit">Pin</button>
                  {row.pinned ? (
                    <button type="button" onClick={() => onUnpin(row.bindingId)}>
                      Unpin
                    </button>
                  ) : null}
                </form>
              ) : null}
            </td>
            <td />
            <td />
            <td>
              <div className={styles.actions}>
                {row.remove ? (
                  <button type="button" onClick={() => onRemove(row.bindingId)}>
                    Remove
                  </button>
                ) : null}
                {row.bringBack ? (
                  <button type="button" onClick={() => onBringBack(row.bindingId)}>
                    Bring back
                  </button>
                ) : null}
                {row.publish ? (
                  <button type="button" onClick={() => onPush(row.streamId)}>
                    Push to KT
                  </button>
                ) : null}
                {row.publish ? (
                  <button type="button" onClick={() => onCancel(row.streamId)}>
                    Cancel
                  </button>
                ) : null}
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function rowClass(row: StreamRowVm): string {
  if (row.dirty) {
    return styles.yellow;
  }

  if (row.deleted) {
    return styles.gray;
  }

  return '';
}

function submitPin(
  event: FormEvent<HTMLFormElement>,
  bindingId: number,
  onPin: (bindingId: number, share: string) => void,
) {
  event.preventDefault();

  const share = String(new FormData(event.currentTarget).get('share') ?? '').trim();
  onPin(bindingId, share);
}
