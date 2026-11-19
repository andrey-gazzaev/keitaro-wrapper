import { useState, type FormEvent } from 'react';
import axios from 'axios';
import type { StreamRowVm } from '@/view-models';
import styles from './campaign-editor.module.css';

type StreamAddProps = {
  /** Live landings streams. Empty when none can take an offer. */
  readonly targets: readonly StreamRowVm[];

  /** Offer name for this id. Rejects when the lookup fails. */
  readonly onLookup: (offerId: number) => Promise<string>;

  /** Binds the offer to the selected stream. */
  readonly onAdd: (streamId: number, offerId: number) => void;
};

/** Landings stream, offer id, and the Add control. */
export function StreamAdd({ targets, onLookup, onAdd }: StreamAddProps) {
  const [offerId, setOfferId] = useState('');
  const [streamId, setStreamId] = useState<number | null>(null);
  const [found, setFound] = useState('');
  const [failure, setFailure] = useState('');

  const known = targets.some((target) => target.streamId === streamId);
  const selected = known && streamId !== null ? streamId : (targets[0]?.streamId ?? null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const parsed = positiveOfferId(offerId);

    if (parsed === null || selected === null) {
      return;
    }

    try {
      const name = await onLookup(parsed);
      setFound(name);
      setFailure('');
      onAdd(selected, parsed);
    } catch (error) {
      setFound('');
      setFailure(lookupFailure(error));
    }
  }

  return (
    <form className={styles.add} onSubmit={submit}>
      <label className={styles.field}>
        Поток
        <select
          value={selected ?? ''}
          onChange={(event) => setStreamId(Number(event.target.value))}
          disabled={targets.length === 0}
        >
          {targets.map((target) => (
            <option key={target.streamId} value={target.streamId}>
              {target.flow === '' ? target.streamId : target.flow}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        Id оффера
        <input value={offerId} onChange={(event) => setOfferId(event.target.value)} />
      </label>

      <button type="submit" disabled={selected === null}>
        Add
      </button>

      {found !== '' ? <p className="status">{found}</p> : null}

      {failure !== '' ? <p className="status">{failure}</p> : null}
    </form>
  );
}

function positiveOfferId(value: string): number | null {
  const trimmed = value.trim();

  if (!/^[1-9]\d*$/.test(trimmed)) {
    return null;
  }

  return Number(trimmed);
}

function lookupFailure(error: unknown): string {
  if (axios.isAxiosError(error) && error.response?.status === 404) {
    return 'Оффер не найден.';
  }

  return 'Keitaro не ответил.';
}
