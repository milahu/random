https://stackoverflow.com/questions/21694167/applying-a-class-to-every-selector-in-a-stylesheet

# Applying a class to every selector in a stylesheet

Aside from using a CSS preprocessor, is there a way to add a class to every selector in a stylesheet, without repeating it?

For example, if I have a stylesheet that looks like this:

```css
#id1 .class1 {
  color: #ccc;
}

#id1 .class2 {
  color: #ddd;
}

#id1 .class3 {
  color: #eee;
}
```

Is there any way I can format it without having to repeat #id1 for every selector?

---

> Aside from using a CSS preprocessor

for comparison, [scss nesting](https://sass-lang.com/guide/#nesting)

```scss
#id1 {
  .class1 { color: #ccc; }
  .class2 { color: #ddd; }
  .class3 { color: #eee; }
}
```

with <code>[sass](https://github.com/sass/dart-sass) src.scss:dst.css</code> this compiles to

```css
#id1 .class1 { color: #ccc; }
#id1 .class2 { color: #ddd; }
#id1 .class3 { color: #eee; }
```
