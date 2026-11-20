import { memo, useCallback, useState, type ChangeEvent, type FormEvent } from 'react';
import { mapOfferFieldError } from '@/mappers';
import { Button, Field, Input } from '@/ui';
import { positiveOfferId } from '@/utils';
import type { StreamRowVm } from '@/view-models';
import { StreamSelect } from './stream-select';
import styles from './stream-add.module.css';

type StreamAddProps = {
  /** Live landings streams. Empty when none can take an offer. */
  readonly targets: readonly StreamRowVm[];

  /** True while the offer is being added. */
  readonly adding: boolean;

  /** Offer name for this id. Rejects when the lookup fails. */
  readonly onLookup: (offerId: number) => Promise<string>;

  /** Binds the offer to the selected stream. */
  readonly onAdd: (streamId: number, offerId: number) => void;
};

/** Landings stream, offer id, and the Add control. */
export const StreamAdd = memo(function StreamAdd({ targets, adding, onLookup, onAdd }: StreamAddProps) {
  const [offerId, setOfferId] = useState('');
  const [streamId, setStreamId] = useState<number | null>(null);
  const [found, setFound] = useState('');
  const [lookupError, setLookupError] = useState<unknown>(null);
  const [offerError, setOfferError] = useState('');

  const known = targets.some((target) => target.streamId === streamId);
  const selected = known && streamId !== null ? streamId : (targets[0]?.streamId ?? null);
  const failure = mapOfferFieldError(lookupError);
  const offerMessage = offerError !== '' ? offerError : failure.offerId;

  const onOffer = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setOfferId(event.target.value);
    setOfferError('');
    setLookupError(null);
  }, []);

  const onStream = useCallback((event: ChangeEvent<HTMLSelectElement>) => {
    setStreamId(Number(event.target.value));
  }, []);

  const submit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const parsed = positiveOfferId(offerId);

      if (parsed === null) {
        setOfferError('Укажите id оффера.');
        setLookupError(null);

        return;
      }

      if (selected === null) {
        return;
      }

      setOfferError('');

      try {
        const name = await onLookup(parsed);
        setFound(name);
        setLookupError(null);
        onAdd(selected, parsed);
      } catch (error) {
        setFound('');
        setLookupError(error);
      }
    },
    [offerId, selected, onLookup, onAdd],
  );

  return (
    <form className={styles.panel} onSubmit={submit}>
      <strong>Добавить оффер</strong>

      <div className={styles.row}>
        <div className={styles.slot}>
          <Field label="Поток" required>
            <StreamSelect targets={targets} selected={selected} onStream={onStream} />
          </Field>
        </div>
        <div className={styles.slot}>
          <Field label="Id оффера" required error={offerMessage}>
            <Input value={offerId} inputMode="numeric" placeholder="106" onChange={onOffer} />
          </Field>
        </div>
        <Button type="submit" variant="primary" disabled={selected === null} pending={adding}>
          Add
        </Button>
      </div>

      {found !== '' ? <p className={styles.found}>{found}</p> : null}
    </form>
  );
});
