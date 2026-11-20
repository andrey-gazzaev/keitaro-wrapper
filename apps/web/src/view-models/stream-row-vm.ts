/** One row in the stream editor table. */
export type StreamRowVm = {
  /** Stable row key. */
  readonly key: string;

  /** Flow cell. Stream name, or the offer name on an offer row. Empty when no name was stored. */
  readonly flow: string;

  /** Working percent with two decimals. Empty on a stream row. */
  readonly share: string;

  /** True when this offer's share is pinned. False on a stream row. */
  readonly pinned: boolean;

  /** True when this offer is removed, or when this stream row is inactive. */
  readonly deleted: boolean;

  /** True when the stream has unpublished changes and the row is yellow. */
  readonly dirty: boolean;

  /** True when this row is the stream itself. False on an offer row. */
  readonly header: boolean;

  /** True when this stream can be chosen in the add control. False for other rows. */
  readonly selectable: boolean;

  /** True when Bring back is shown for a removed offer on a live stream, or for an inactive stream row. */
  readonly bringBack: boolean;

  /** True when Remove is shown for this live offer. */
  readonly remove: boolean;

  /** True when this live offer can be pinned or unpinned. */
  readonly pin: boolean;

  /** True when this stream row shows Push to KT and Cancel. */
  readonly publish: boolean;

  /** Binding id for offer actions. Zero on a stream row, which has no binding. */
  readonly bindingId: number;

  /** Stream id for bring back, push, cancel, and the add select. */
  readonly streamId: number;
};
