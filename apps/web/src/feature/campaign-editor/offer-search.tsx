import { useState, type ChangeEvent, type ReactNode } from 'react';
import { mapOfferFieldError } from '@/mappers';
import type { Offer } from '@/models';
import { useSearchOffers } from '@/queries';
import { Field, Input } from '@/ui';
import styles from './offer-search.module.css';
import { useDebounce } from './use-debounce';

type OfferSearchProps = {
  /** Message under the field. Empty when the choice is fine. */
  readonly error: string;

  /** Chosen offer. Null when the text changes or nothing is chosen. */
  readonly onOffer: (offer: Offer | null) => void;
};

/** Search field and up to ten matching offers. */
export function OfferSearch({ error, onOffer }: OfferSearchProps) {
  const [text, setText] = useState('');
  const [picked, setPicked] = useState<Offer | null>(null);
  const needle = useDebounce(text.trim(), 300);
  const search = useSearchOffers(needle);

  const trimmed = text.trim();
  const settled = trimmed !== '' && trimmed === needle;
  const failure = mapOfferFieldError(settled ? search.error : null);
  const inFlight = settled && search.isFetching;
  const rows = settled && !inFlight && failure.offerId === '' && search.isSuccess ? (search.data ?? []) : [];

  const onText = (event: ChangeEvent<HTMLInputElement>) => {
    setText(event.target.value);
    setPicked(null);
    onOffer(null);
  };

  const pick = (offer: Offer) => {
    setPicked(offer);
    onOffer(offer);
  };

  let menuItem: ReactNode = null;

  if (inFlight) {
    menuItem = <li className={styles.status}>Поиск…</li>;
  } else if (failure.offerId !== '') {
    menuItem = <li className={styles.status}>{failure.offerId}</li>;
  } else if (settled && search.isSuccess && rows.length === 0) {
    menuItem = <li className={styles.status}>Ничего не найдено</li>;
  } else if (rows.length > 0) {
    menuItem = rows.map((offer) => (
      <li key={offer.id}>
        <button
          type="button"
          className={styles.option}
          role="option"
          aria-selected={picked?.id === offer.id}
          onClick={() => pick(offer)}
        >
          {offer.id} {offer.name}
        </button>
      </li>
    ));
  }

  const menu =
    menuItem === null ? null : (
      <ul className={styles.menu} role="listbox">
        {menuItem}
      </ul>
    );

  return (
    <div className={styles.search}>
      <Field label="Оффер" required error={error}>
        <div className={styles.anchor}>
          <Input value={text} onChange={onText} />

          {menu}
        </div>
      </Field>
    </div>
  );
}
