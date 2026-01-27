import Dexie, { type Table } from 'dexie';
import type { Material, CourseCard, View, UserRole } from '../types';

export interface AppState {
    id: string; // constant 'current'
    view: View;
    role?: UserRole;
    isLoggedIn: boolean;
    activeCourseId?: string;
    lastUpdated: Date;
}

export class IITUDatabase extends Dexie {
    materials!: Table<Material>;
    courses!: Table<CourseCard>;
    appState!: Table<AppState>;
    chatHistory!: Table<{ id?: number; courseId: string; title: string; timestamp: Date; messages: any[] }>;

    constructor() {
        super('IITUTeacherDatabase');
        this.version(2).stores({ // Bump version
            materials: 'id, name, status, uploadedAt',
            courses: 'id, subject, teacherName',
            appState: 'id',
            chatHistory: '++id, courseId, timestamp'
        });
    }
}

export const db = new IITUDatabase();

// Helper to save app state
export async function saveAppState(state: Partial<AppState>) {
    const current = await db.appState.get('current');
    await db.appState.put({
        id: 'current',
        view: 'welcome',
        isLoggedIn: false,
        lastUpdated: new Date(),
        ...current,
        ...state,
    });
}

// Helper to load app state
export async function loadAppState(): Promise<AppState | undefined> {
    return await db.appState.get('current');
}
