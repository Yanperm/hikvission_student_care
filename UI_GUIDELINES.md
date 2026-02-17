# macOS UI Design System

## 🎨 สี (Colors)

```css
--macos-blue: #007aff     /* Primary Actions */
--macos-green: #34c759    /* Success */
--macos-orange: #ff9500   /* Warning */
--macos-red: #ff3b30      /* Danger */
--macos-purple: #af52de   /* Special */
```

## 📐 Layout

### Sidebar
- Width: 240px
- Glass effect with blur
- Fixed position

### Cards
- Border-radius: 16px
- Padding: 24px
- Glass effect

### Spacing
- Small: 8px
- Medium: 16px
- Large: 24px

## 🔤 Typography

- Font: SF Pro Display / Inter
- Heading: 24px, 600 weight
- Body: 13px, 400 weight
- Small: 12px

## 🎭 Components

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Danger</button>
```

### Cards
```html
<div class="card">
    <h2>Title</h2>
    <p>Content</p>
</div>
```

### Badges
```html
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-danger">Error</span>
```

## 📱 Responsive

- Desktop: Full sidebar
- Mobile: Collapsible sidebar
- Breakpoint: 768px

## ✨ Animations

- Transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1)
- Hover: translateY(-2px)
- Scale: 1.02

## 🎯 Best Practices

1. ใช้ Glass effect สำหรับ cards
2. ใช้ SF Pro Display font
3. Spacing ต้องสม่ำเสมอ
4. Animation ต้องนุ่มนวล
5. สี contrast ต้องชัดเจน
