import { memo, useCallback, useMemo, useState, type ChangeEvent, type FormEvent } from 'react';
import axios from 'axios';
import type { StreamRowVm } from '@/view-models';
import { Button, Field } from '@/ui';
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
export const StreamAdd = memo(function StreamAdd({ targets, onLookup, onAdd }: StreamAddProps) {
  const [offerId, setOfferId] = useState('');
  const [streamId, setStreamId] = useState<number | null>(null);
  const [found, setFound] = useState('');
  const [failure, setFailure] = useState('');

  const known = targets.some((target) => target.streamId === streamId);
  const selected = known && streamId !== null ? streamId : (targets[0]?.streamId ?? null);

  const onOffer = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setOfferId(event.target.value);
  }, []);

  const onStream = useCallback((event: ChangeEvent<HTMLSelectElement>) => {
    setStreamId(Number(event.target.value));
  }, []);

  const submit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
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
    },
    [offerId, selected, onLookup, onAdd],
  );

  const streamSelect = useMemo(
    () => (
      <select value={selected ?? ''} onChange={onStream} disabled={targets.length === 0}>
        {targets.map((target) => (
          <option key={target.streamId} value={target.streamId}>
            {target.flow === '' ? target.streamId : target.flow}
          </option>
        ))}
      </select>
    ),
    [targets, selected, onStream],
  );

  const offerInput = useMemo(
    () => <input value={offerId} inputMode="numeric" placeholder="106" onChange={onOffer} />,
    [offerId, onOffer],
  );

  return (
    <form className={styles.panel} onSubmit={submit}>
      <strong>Добавить оффер</strong>

      <div className={styles.row}>
        <div className={styles.slot}>
          <Field label="Поток">{streamSelect}</Field>
        </div>
        <div className={styles.slot}>
          <Field label="Id оффера">{offerInput}</Field>
        </div>
        <Button type="submit" variant="primary" disabled={selected === null}>
          Add
        </Button>
      </div>

      {found !== '' ? <p className={styles.found}>{found}</p> : null}

      {failure !== '' ? <p className="status">{failure}</p> : null}
    </form>
  );
});

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
