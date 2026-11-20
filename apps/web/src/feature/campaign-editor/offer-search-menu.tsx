import { memo } from 'react';
import type { Offer } from '@/models';
import { OfferSearchMenuItems } from './offer-search-menu-items';
import styles from './offer-search-menu.module.css';

type OfferSearchMenuProps = {
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

/** Offer list. Hidden until there is a status or at least one match. */
export const OfferSearchMenu = memo(function OfferSearchMenu({
  inFlight,
  message,
  empty,
  offers,
  pickedId,
  onPick,
}: OfferSearchMenuProps) {
  const open = inFlight || message !== '' || empty || offers.length > 0;

  if (!open) {
    return null;
  }

  return (
    <ul className={styles.menu} role="listbox">
      <OfferSearchMenuItems
        inFlight={inFlight}
        message={message}
        empty={empty}
        offers={offers}
        pickedId={pickedId}
        onPick={onPick}
      />
    </ul>
  );
});
