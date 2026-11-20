import { memo, useCallback, useState, type ChangeEvent } from 'react';
import { mapOfferFieldError } from '@/mappers';
import type { Offer } from '@/models';
import { useSearchOffers } from '@/queries';
import { Field, Input } from '@/ui';
import { OfferSearchMenu } from './offer-search-menu';
import styles from './offer-search.module.css';
import { useDebounce } from './use-debounce';

const NO_OFFERS: readonly Offer[] = [];

type OfferSearchProps = {
  /** Message under the field. Empty when the choice is fine. */
  readonly error: string;

  /** Chosen offer. Null when the text changes or nothing is chosen. */
  readonly onOffer: (offer: Offer | null) => void;
};

/** Search field and up to ten matching offers. */
export const OfferSearch = memo(function OfferSearch({ error, onOffer }: OfferSearchProps) {
  const [text, setText] = useState('');
  const [picked, setPicked] = useState<Offer | null>(null);
  const [lookup, setLookup] = useState('');
  const needle = useDebounce(lookup.trim(), 300);
  const search = useSearchOffers(needle);

  const trimmed = text.trim();
  const settled = picked === null && trimmed !== '' && trimmed === needle;
  const failure = mapOfferFieldError(settled ? search.error : null);
  const inFlight = settled && search.isFetching;
  const offers =
    settled && !inFlight && failure.offerId === '' && search.isSuccess ? (search.data ?? NO_OFFERS) : NO_OFFERS;
  const empty = settled && search.isSuccess && offers.length === 0;
  const pickedId = picked?.id ?? null;

  const onText = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const next = event.target.value;

      setText(next);
      setLookup(next);
      setPicked(null);
      onOffer(null);
    },
    [onOffer],
  );

  const pick = useCallback(
    (offer: Offer) => {
      setText(offer.name);
      setPicked(offer);
      onOffer(offer);
    },
    [onOffer],
  );

  return (
    <div className={styles.search}>
      <Field label="Оффер" required error={error}>
        <div className={styles.anchor}>
          <Input value={text} onChange={onText} />

          <OfferSearchMenu
            inFlight={inFlight}
            message={failure.offerId}
            empty={empty}
            offers={offers}
            pickedId={pickedId}
            onPick={pick}
          />
        </div>
      </Field>
    </div>
  );
});
