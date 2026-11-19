import type { StreamGroup } from '@/models';
import type { StreamGroupDto } from '../../schemas/editor/stream-group.schema';
import { mapStreamLine } from './map-stream-line';

/** Stream from an editor stream JSON body. */
export function mapStreamGroup(dto: StreamGroupDto): StreamGroup {
  return {
    id: dto.id,
    name: dto.name,
    position: dto.position,
    acceptsOffers: dto.accepts_offers,
    deleted: dto.deleted,
    dirty: dto.dirty,
    lines: dto.lines.map(mapStreamLine),
  };
}
