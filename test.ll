


define i32 @main() {
    %buffer1 = icmp slt i32 1, 2
    br i1 %buffer1, label %lab.0, label %lab.1
lab.0:
    %lab.ptr = alloca i32
    store i32 1, i32* %lab.ptr
    %b.ptr = alloca i32
    %lab.2 = load i32, i32* %lab.ptr
    %buffer3 = add i32 %lab.2, 1
    store i32 %buffer3, i32* %b.ptr
    br label %lab.2
lab.1:
    br label %lab.2
lab.2:
    ret i32 0
}

declare i32 @printf(i8*, ...)
