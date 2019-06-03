


define i32 @main() {
    %n.ptr = alloca i32
    store i32 5, i32* %n.ptr
    %arr.ptr = alloca [123 x i32]
    %n.ptr.1 = load i32, i32* %n.ptr.ptr
    %n.ptr.1.2 = load i32, i32* %n.ptr.1.ptr
    %arr.3.ptr = getelementptr inbounds [123 x i32], [123 x i32]* %arr.ptr, i32 0, i32 %n.ptr.1.2
    store i32 1, i32* %arr.3.ptr
    ret i32 0
}

declare i32 @printf(i8*, ...)
