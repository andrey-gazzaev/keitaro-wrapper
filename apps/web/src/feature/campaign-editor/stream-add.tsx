import { memo, useCallback, useState, type ChangeEvent, type FormEvent } from 'react';
import type { Offer } from '@/models';
import { Button, Field } from '@/ui';
import type { StreamRowVm } from '@/view-models';
import { OfferSearch } from './offer-search';
import { StreamSelect } from './stream-select';
import styles from './stream-add.module.css';

type StreamAddProps = {
  /** Live landings streams. Empty when none can take an offer. */
  readonly targets: readonly StreamRowVm[];

  /** True while the offer is being added. */
  readonly adding: boolean;

  /** Binds the offer to the selected stream. */
  readonly onAdd: (streamId: number, offerId: number) => void;
};

/** Landings stream, offer search, and the Add control. */
export const StreamAdd = memo(function StreamAdd({ targets, adding, onAdd }: StreamAddProps) {
  const [streamId, setStreamId] = useState<number | null>(null);
  const [offer, setOffer] = useState<Offer | null>(null);
  const [offerError, setOfferError] = useState('');

  const known = targets.some((target) => target.streamId === streamId);
  const selected = known && streamId !== null ? streamId : (targets[0]?.streamId ?? null);

  const onOffer = useCallback((next: Offer | null) => {
    setOffer(next);
    setOfferError('');
  }, []);

  const onStream = useCallback((event: ChangeEvent<HTMLSelectElement>) => {
    setStreamId(Number(event.target.value));
  }, []);

  const submit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      if (offer === null) {
        setOfferError('Выберите оффер');

        return;
      }

      if (selected === null) {
        return;
      }

      setOfferError('');
      onAdd(selected, offer.id);
    },
    [offer, selected, onAdd],
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

        <div className={styles.offer}>
          <OfferSearch error={offerError} onOffer={onOffer} />
        </div>

        <Button type="submit" variant="primary" disabled={selected === null} pending={adding}>
          Add
        </Button>
      </div>
    </form>
  );
});
