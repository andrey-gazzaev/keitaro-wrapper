import type { StreamLine } from '@/models';
import type { StreamLineDto } from '../../schemas/editor/stream-line.schema';

/** Offer row from an editor line JSON body. */
export function mapStreamLine(dto: StreamLineDto): StreamLine {
  return {
    id: dto.id,
    offerId: dto.offer_id,
    name: dto.name,
    share: dto.share,
    pinned: dto.pinned,
    deleted: dto.deleted,
  };
}
