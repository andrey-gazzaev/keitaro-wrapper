import { memo } from 'react';
import type { Offer } from '@/models';
import styles from './offer-search-menu-items.module.css';

type OfferSearchMenuItemsProps = {
  /** True while the settled search is still running. */
  readonly inFlight: boolean;

  /** Failure text. Empty when the search has not failed. */
  readonly message: string;

  /** True when a finished search returned no offers. */
  readonly empty: boolean;

  /** Matching offers. Empty when there is nothing to choose. */
  readonly offers: readonly Offer[];

  /** Chosen offer id. Null when nothing is chosen. */
  readonly pickedId: number | null;

  /** Stores the chosen offer. */
  readonly onPick: (offer: Offer) => void;
};

/** Status line, or one button per matching offer. */
export const OfferSearchMenuItems = memo(function OfferSearchMenuItems({
  inFlight,
  message,
  empty,
  offers,
  pickedId,
  onPick,
}: OfferSearchMenuItemsProps) {
  if (inFlight) {
    return <li className={styles.status}>Поиск…</li>;
  }

  if (message !== '') {
    return <li className={styles.status}>{message}</li>;
  }

  if (empty) {
    return <li className={styles.status}>Ничего не найдено</li>;
  }

  return offers.map((offer) => (
    <li key={offer.id}>
      <button
        type="button"
        className={styles.option}
        role="option"
        aria-selected={pickedId === offer.id}
        onClick={() => onPick(offer)}
      >
        {offer.id} {offer.name}
      </button>
    </li>
  ));
});
