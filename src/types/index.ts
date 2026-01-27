export type UserRole = 'student' | 'teacher';
export type View = 'welcome' | 'auth' | 'student' | 'dashboard';

export interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
}

export interface Teacher extends User {
    role: 'teacher';
    bio?: string;
    department?: string;
}

export interface Material {
    id: string;
    name: string;
    type: string;
    size: string;
    status: 'pending' | 'processing' | 'ready' | 'error';
    progress: number;
    uploadedAt: Date;
}

export interface CourseCard {
    id: string;
    subject: string;
    teacherName: string;
    teacherId: string;
    description: string;
    materialsCount: number;
    studentCount: number;
    lastTrained?: Date;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export interface ChatSession {
    id: string;
    courseId: string;
    messages: Message[];
}
